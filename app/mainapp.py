import time
from PySide2.QtCore import, QObject, QRunnable, QThreadPool, Signal, Slot
from PySide2.QtGui import QIcon
#Don't include tools I can't (or shouldn't) upload
try:
    from app.workflow_tool.infringing_tools import BaseTool,TOOLS,ToolRunException
except ImportError:
    from app.workflow_tool.tools import BaseTool,TOOLS,ToolRunException
from typing import List, TextIO
from PySide2 import QtCore, QtGui,QtMultimedia
from PySide2.QtWidgets import QApplication, QComboBox, QInputDialog,QMainWindow, QSpacerItem,QListWidgetItem,QLabel,QLineEdit,QFileDialog,QPushButton,QHBoxLayout,QSpinBox
from daiquiri.formatter import ColorExtrasFormatter
from app.main_ui import Ui_MainWindow
import sys,os
import shutil
import daiquiri
import configparser
import humanize
import traceback
from queue import Queue,Empty
from datetime import datetime,timedelta
from json2html import json2html
from app.utils import file_str, get_video_info, local_path,script_dir,make_dirs,normalize_extension,list_get
from app.custom_widgets import Droppable_button, Droppable_lineEdit

LOG_PATH=os.path.join(script_dir(),'data','logs',datetime.now().strftime('%Y%m%d_%H%M%S')+'_workflow_tool.log')

def _make_log_file(): return daiquiri.output.RotatingFile(LOG_PATH,formatter=daiquiri.formatter.TEXT_FORMATTER,level=daiquiri.logging.DEBUG,max_size_bytes=20*1024*1024,backup_count=5)
def setup_logging(stream):
    make_dirs(LOG_PATH)
    daiquiri.setup(level=daiquiri.logging.INFO,outputs=(
        daiquiri.output.Stream(),
        daiquiri.output.Stream(stream=stream,formatter=ColorExtrasFormatter(fmt='%(asctime)s %(color)s%(levelname)-8.8s: %(message)s%(color_stop)s %(extras)s',datefmt='%I:%M:%S %p'))
    ))
logger=daiquiri.getLogger('workflow-tool')

RESOURCES_DIR=local_path('resources')
#load config 
config_path=os.path.join(script_dir(),'data','config.ini')
config=configparser.SafeConfigParser(allow_no_value=True)

class OutputStream(TextIO):
    colors={
        "\033[00;32m":"LawnGreen",  # GREEN
         "\033[00;36m":"DeepSkyBlue",  # CYAN
        "\033[01;33m":"Orange",  # BOLD YELLOW
        "\033[01;31m":"Crimson",  # BOLD RED
         "\033[01;31m":"Crimson",  # BOLD RED
         "\x1b[00;32m":"LawnGreen",  # GREEN
         "\x1b[00;36m":"DeepSkyBlue",  # CYAN
        "\x1b[01;33m":"Orange",  # BOLD YELLOW
        "\x1b[01;31m":"Crimson",  # BOLD RED
         "\x1b[01;31m":"Crimson",  # BOLD RED
        }
    def __init__(self,callback):
        super(OutputStream,self).__init__()
        self.callback=callback
    def isatty(self):return True
    def write(self,text:str):
        text=text.strip()
        text='<p style="margin:0;">'+text
        for key,val in self.colors.items():
            if key in text:
                text=text.replace(key,f'<span style="font-weight:bold;color:{val};">')
        text=(text.replace('\x1b[0m','</span>')+'</p>').replace('\n','<br>').replace('\r','')
        self.callback(text)

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress 

    '''
    finished = Signal()
    canceled=Signal(str)
    error = Signal(Exception)
    result = Signal(object)
    progress = Signal(int)

class ToolWorker(QRunnable):
    def __init__(self,file:list,output:str,tool:BaseTool,options:dict,threads:int,*args,**kwargs):
        QRunnable.__init__(self)
    
        self.signals=WorkerSignals()
        self.file,self.output,self.options,self.threads=file,output,options,threads
        self.tool:BaseTool=tool()
        self.tool.percent_callback=self.signals.progress.emit
        self.args=args
        self.kwargs=kwargs
        self._canceled=False
        self._done_callback=lambda:None
    @Slot()
    def run(self):
        try:
            # logger.info(file)
            result = self.tool.run(self.file,self.output,self.options,self.threads, **self.kwargs)
        except Exception as e:
             self.signals.error.emit(e)
        else:
            if not self._canceled: self.signals.result.emit(result)  # Return the result of the processing
            else: self.signals.canceled.emit(self.output)
        finally:
            self.signals.finished.emit()  # Done
            self._done_callback()

    @Slot()
    def stop(self):
        self._canceled=True
        self.tool.stop()


class ThreadQueue(QRunnable):
    def __init__(self,thread_pool:QThreadPool):
        QRunnable.__init__(self)
        self.thread_pool:QThreadPool=thread_pool
        self.thread_queue=Queue()
        self._stop=False
        self.thread_running=False
        self.current_runner=None

    @Slot()
    def run(self):
        while not self._stop:
            try:
                if not self.thread_running:
                    runner:ToolWorker=self.thread_queue.get(timeout=0.5)
                    self.current_runner=runner
                    runner._done_callback=self._thread_finished
                    self.thread_pool.start(runner)
                    self.thread_running=True
                else:time.sleep(0)
            except Empty:
                self.current_runner=None
                time.sleep(0)


    def add(self,runner:QRunnable):
        self.thread_queue.put_nowait(runner)

    @Slot()
    def stop(self,exiting:False):
        if exiting: self._stop=True
        if self.current_runner:
            self.current_runner.stop()
        with self.thread_queue.mutex:
            self.thread_queue.queue.clear()
            self.thread_queue.all_tasks_done.notify_all()
            self.thread_queue.unfinished_tasks = 0
        print()
    def _thread_finished(self):
        self.thread_running=False
    
    





#TODO
#     Allow drag/drop onto file inputs
#     Add workflow page and "workflow parser" (eg: extract audio -> level audio -> insert audio)
#     Add creationflags = CREATE_NO_WINDOW to every subprocess.Popen to stop from opening console window
#     Trim imports to reduce size
#     Reorganize resources folder (eg: binaries to "libs" folder)
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(RESOURCES_DIR,'icon.ico')))
        self.tools:List[BaseTool]=None
        
        #debug stuff
        setup_logging(OutputStream(self.ui.text_output.append))
        #config
        self.load_config()
        self.sound_effect=QtMultimedia.QSoundEffect(None)
        #buttons
        self.ui.action_ee.triggered.connect(self.play_ee)
        self.ui.action_set_threads.triggered.connect(lambda: config.set('processing','threads',
        str(QInputDialog.getInt(self,'Threads','Number of threads to use:',os.cpu_count(),1,os.cpu_count())[0]) or config.getint('processing','threads')))
        self.ui.action_save_config.triggered.connect(lambda: self.save_config())
        self.ui.action_reload_config.triggered.connect(lambda: self.load_config())
        self.ui.info_browser_button.clicked.connect(lambda: self.ui.info_file_text.setText(
            QFileDialog.getOpenFileName(self,'File to get info on','.','Media Files (*)')[0]))
        self.ui.info_file_text.textChanged.connect(self.show_file_info)
        self._last_files_text=None
        self.ui.info_browser_button.files_dropped.connect(self.ui.info_file_text.setText)
        self.ui.info_file_text.files_dropped.connect(self.ui.info_file_text.setText)
        #loading
        self.load_tools()
        #worker stuff
        self.thread_pool = QThreadPool()
        self.thread_queue=ThreadQueue(self.thread_pool)
        self.thread_pool.start(self.thread_queue)
        logger.info('Ready!')
    #Boilerplate====================================================
    def event(self, e):
        # This is all for that ambient statustip message. Was it worth it? Who knows
        if e.type() == QtCore.QEvent.StatusTip:
            if e.tip() == '':
                e = QtGui.QStatusTipEvent('The ultimate all-in one tool')
        return super().event(e)
    
    def load_config(self):
        """Load the config file
        """
        if not os.path.exists(config_path):
            make_dirs(config_path)
            default_config_path=os.path.join(RESOURCES_DIR,'default_config.ini')
            shutil.copy(default_config_path,config_path)
            logger.info(f'Wrote default config to {config_path}')
        config.clear()
        config.read(config_path)
        try:
            #general
            #start tab
            d=config.get('general','start_tab')
            if d not in ('workflow','tools','video_info'): 
                config.set('general','start_tab','workflow')
                d=config.get('general','start_tab')
            if d=='workflow':self.ui.tabs.setCurrentIndex(0)
            else:self.ui.tabs.setCurrentIndex(1)

            #log files
            d=config.getboolean('general','create_log_files')
            if d is None:
                config.set('general','create_log_files','false')
                d=config.getboolean('general','create_log_files')
            if d: logger.logger.addHandler(_make_log_file().handler)
            if d: logger.info(f'Logging to {LOG_PATH}')    

            #log level
            d=config.get('general','log_level')
            if d not in ('debug','info','warn','error','critical'):
                config.set('general','log_level','info')
                d=config.get('general','log_level')
            logger.setLevel(d.upper())
            logger.debug(f'Set log level to {d.upper()}')

            

            #processing
            d=config.getint('processing','threads')
            if d is None:
                config.set('processing','threads',str(os.cpu_count()))
                d=config.getboolean('processing','threads')
        except Exception as e:
            logger.error(f"Couldn't load config file",error=e,file=config_path)
        logger.info('Loaded config')

    def save_config(self):
        with open(config_path,'w') as f:
            config.write(f)
        logger.info(f'Saved config {config_path}')

    def play_ee(self):
        if self.sound_effect.isPlaying():
            self.sound_effect.stop()
            self.ui.action_ee.setText('Don\'t click this again...')
        else:
            logger.error('You clicked the thing...')
            self.ui.action_ee.setText(r'I told you not to ¯\_(ツ)_/¯')
            self.sound_effect.setVolume(0.1)
            self.sound_effect.setSource(QtCore.QUrl.fromLocalFile(os.path.join(RESOURCES_DIR,'audio','ee.wav')))
            self.sound_effect.play()

    def play_sound_effect(self,sound:str,volume:float=0.2):
        """Play the given sound effect

        Args:
            sound (str): The path to the .wav file to play
            volume (float, optional): The volume to play at. Defaults to 0.2.
        """
        if self.sound_effect.isPlaying():
            self.sound_effect.stop()
        self.sound_effect.setVolume(volume)
        self.sound_effect.setSource(QtCore.QUrl.fromLocalFile(sound))

    def closeEvent(self,e):
        self.thread_queue.stop(True)
        # with open(config_path,'w') as f:
        #     config.write(f)
        ...
    
    def clear_layout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())
    
    def pick_files(self,files=None,types="Any(*)",type_desc:str=None,single_file:bool=False):
        """
        Gather files, either from a file dialog or from the provided list of files
        """
        types_text=f'{type_desc or "Files"} ('+" ".join(f'*.{t}' for t in types)+');;Any(*)'
        if not single_file:
            if not files:
                file_paths=QFileDialog.getOpenFileNames(self,'Choose a file (or files)','.',types_text)[0]
            else:
                file_paths= [f for f in files.split(';') if normalize_extension(os.path.splitext(f)[1],False) in types]
        else:
            if not files:
                file_paths=[QFileDialog.getOpenFileName(self,'Choose a file','.',types_text)[0] ,]
            else:
                try:
                    file_paths= [[f for f in files.split(';') if normalize_extension(os.path.splitext(f)[1],False) in types][0],]
                except IndexError:
                    file_paths=[]
            
        return file_paths
        

    def pick_dir(self):
        return QFileDialog.getExistingDirectory(self,'Choose an output directory','')

    #Tool stuff=====================================================
    def load_tools(self):
        self.tools=TOOLS
        tools_list=self.ui.tools_list
        
        for tool_name,tool in self.tools:
            item=QListWidgetItem(icon=None)
            item.setText(f'{tool_name} '+(f'({",".join(str(f) for f in tool.allowed_inputs)})'.replace("'",'') if tool.allowed_inputs else ''))
            item.setData(1,tool)
            item.setStatusTip(tool.description)
            item.setToolTip(tool.description)
            self.ui.tools_list.addItem(item)
        self.ui.tools_list.itemClicked.connect(self.show_single_tool)
        self.ui.tools_list.setCurrentRow(0)
        self.show_single_tool(self.ui.tools_list.currentItem())
        logger.info(f'Loaded {len(self.tools)} tools')

    def show_single_tool(self,tool_widget:QListWidgetItem):
        logger.debug(f'{tool_widget.text().split("(")[0].strip()} selected')
        tool:BaseTool=tool_widget.data(1)
        logger.debug(f'Got tool class {tool}')
        layout=self.ui.tools_tab_layout
        layout.setVerticalSpacing(3)
        self.clear_layout(layout)

        #info
        label=QLabel(tool_widget.text().split('(')[0].strip()+': '+tool.description)
        layout.addRow(label)
        
        # inputs=QLabel('Inputs: '+','.join(str(f) for f in tool.allowed_inputs).replace("'",''))
        # outputs=QLabel('Outputs: '+','.join(str(f) for f in tool.allowed_outputs).replace("'",''))
        # layout.addRow(inputs)
        # layout.addRow(outputs)

        #input files
        browse=Droppable_button()
        browse.files_dropped.connect(lambda files:files_text.setText(';'.join(self.pick_files(files=files,types=allowed_inputs_1,type_desc='Video/Audio files',single_file=tool.single_file))))

        browse.setObjectName('tools_tab_browse_button')
        browse.setText('Browse...')
        browse.setStatusTip('Browse for file(s)')
        files_text=Droppable_lineEdit()
        files_text.setAcceptDrops(True)
        files_text.files_dropped.connect(lambda files:files_text.setText(';'.join(self.pick_files(files=files,types=allowed_inputs_1,type_desc='Video/Audio files',single_file=tool.single_file))))
        files_text.setObjectName('tools_tab_file_text')
        allowed_inputs_1=tool.allowed_inputs if len(tool.allowed_inputs)==0 or type(tool.allowed_inputs[0])!=tuple else tool.allowed_inputs[0]
        files_text.setPlaceholderText(f'File{"" if tool.single_file else "s"}... '+(f'({",".join("."+t for t in allowed_inputs_1)})'if allowed_inputs_1 else '') )
        files_text.setStatusTip(f'File{"" if tool.single_file else "s"} to process')
        def _ft(s):self._last_files_text=s
        self._last_files_text
        files_text.textChanged.connect(_ft)
        browse.clicked.connect(lambda: files_text.setText(';'.join(self.pick_files(types=allowed_inputs_1,type_desc='Video/Audio files',single_file=tool.single_file))))
        files_layout=QHBoxLayout()
        files_layout.addWidget(files_text)
        files_layout.addWidget(browse)
        layout.addRow(f'Input File{"" if tool.single_file else "s"}:',files_layout)

        #output
        output_browse=QPushButton()
        output_browse.setObjectName('tools_tab_output_browse_button')
        output_browse.setText('Browse...')
        output_browse.setStatusTip('Browse for folder')
        output_folder_text=QLineEdit()
        output_folder_text.setObjectName('tools_tab_output_folder_text')
        output_folder_text.setPlaceholderText('Folder...')
        output_folder_text.setStatusTip('Folder to output to')
        output_folder_text.setReadOnly(True)
        output_browse.clicked.connect(lambda: output_folder_text.setText(self.pick_dir()+'/*'+normalize_extension(output_filetype.text())))
        files_text.textChanged.connect(lambda t:output_folder_text.setText(os.path.dirname(t.split(';')[0])+'*'+normalize_extension(output_filetype.text())) )

        if tool.allowed_outputs:
            output_filetype=QComboBox()
            output_filetype.text=output_filetype.currentText
            output_filetype.setStatusTip('File type to output/convert to')
            output_filetype.addItems('.'+t for t in tool.allowed_outputs)
            output_filetype.currentTextChanged.connect(lambda t:output_folder_text.setText(output_folder_text.text().split('*')[0]+f'*{normalize_extension(t)}'))
        else:
            output_filetype=QLineEdit()
            output_filetype.setStatusTip('File type to output/convert to')
            output_filetype.textChanged.connect(lambda t:output_folder_text.setText(output_folder_text.text().split('*')[0]+f'*{normalize_extension(t)}'))

        output_folder_layout=QHBoxLayout()
        output_folder_layout.addWidget(output_folder_text)
        output_folder_layout.addWidget(output_browse)
        output_folder_layout.addWidget(output_filetype)
        layout.addRow('Output:',output_folder_layout)

        #create options
        option_objects={}
        logger.debug(f'Required Options: {str(tool.required_options)}')
        for opt in tool.required_options:
            opt_name,opt_type=opt
            opt_widget=None
            #option types
            #number required
            if opt_type==int:
                opt_widget=QSpinBox()
                opt_widget.setStatusTip(f'Select {opt_name.lower()}...')
                opt_widget.text=opt_widget.value

            #string required
            elif opt_type==str:
                opt_widget=QLineEdit()
                opt_widget.setStatusTip(f'Enter {opt_name.lower()}...')

            #option from list required
            elif type(opt_type) in (tuple,list):
                opt_widget=QComboBox()
                opt_widget.addItems(opt_type)
                opt_widget.text=opt_widget.currentText
                opt_widget.setStatusTip(f'Select {opt_name.lower()}...')
            #file required
            elif opt_type==file_str:
                allowed_inputs_2=tool.allowed_inputs[1]
                opt_browse=Droppable_button()
                opt_browse.setText('Browse...')
                opt_file_text=Droppable_lineEdit()
                opt_file_text.files_dropped.connect(lambda files: 
                    opt_file_text.setText(';'.join(self.pick_files(files=files,types=allowed_inputs_2,type_desc='Video/Audio files',single_file=tool.single_file))))
                opt_file_text.setPlaceholderText(f'File{"" if tool.single_file else "s"}... ({",".join("."+t for t in allowed_inputs_2)})')
                opt_browse.clicked.connect(lambda: 
                    opt_file_text.setText(';'.join(self.pick_files(types=allowed_inputs_2,type_desc='Video/Audio files',single_file=tool.single_file))))
                opt_browse.files_dropped.connect(lambda files: 
                    opt_file_text.setText(';'.join(self.pick_files(files=files,types=allowed_inputs_2,type_desc='Video/Audio files',single_file=tool.single_file))))
                opt_browse.setStatusTip(f'Browse for {opt_name.lower()}...')
                opt_file_text.setStatusTip(f'{opt_name}...')
                opt_widget=QHBoxLayout()
                opt_widget.addWidget(opt_file_text)
                opt_widget.addWidget(opt_browse)
                option_objects[opt_name]=opt_file_text
            opt_widget.setObjectName(opt_name)
            layout.addRow(opt_name,opt_widget)

            if opt_name not in option_objects: option_objects[opt_name]=opt_widget
        
        run_button=QPushButton()
        run_button.setText('Run')
        run_button.setStatusTip('Run tool on files')

        cancel_button=QPushButton()
        cancel_button.setText('Cancel')
        cancel_button.setStatusTip('Cancel processing')
        cancel_button.setDisabled(True)
        cancel_button.clicked.connect(self.cancel_processing)

        run_button.clicked.connect(lambda: self.processFiles(files_text.text().split(';'),output_folder_text.text(),output_filetype.text(),tool,option_objects,run_button,cancel_button))
        btns_layout=QHBoxLayout()
        btns_layout.addWidget(run_button)
        btns_layout.addWidget(cancel_button)

        layout.addRow('Process:',btns_layout)
        spacer=QSpacerItem(self.ui.tools_tab.geometry().width()//2,1)
        layout.addItem(spacer)

        #carry-over text
        if self._last_files_text:
            last_ext=normalize_extension(os.path.splitext(self._last_files_text.split(';')[0])[1],False)
            if not allowed_inputs_1 or last_ext in (allowed_inputs_1):
                files_text.setText(self._last_files_text)
            else: self._last_files_text=None

    def processFiles(self,files:list,output_folder:str,output_type,tool:BaseTool,option_objects:dict,run_button:QPushButton,cancel_button:QPushButton):
        while '' in files:files.remove('')
        if not files:
            logger.error(f'No input file(s) selected')
            return
        options={}
        for key,val in option_objects.items():
            options[key]=val.text()
            if type(options[key]) in (str,) and ';' in options[key]:
                options[key]=options[key].split(';')

        logger.info(f'Running {tool.__name__} on {len(files)} file{"s" if len(files)>1 else ""}...')
        logger.debug(f'Inputs:',files=files)
        output_dir,_=output_folder.split('*')
        logger.debug(f'Output dir:',output_dir=output_dir)
        logger.debug(f'Output type:',output_type=output_type)
        # logger.info('Starting',files=files,output_folder=output_folder,output_type=output_type,tool=type(tool),options=options)

        #start worker

        multi_options={k:v for k,v in options.items() if type(v) in (tuple,list)}
        for i,file in enumerate(files):
            if multi_options:
                for k,v in multi_options.items():
                    options[k]=v[i]

            output=f'{os.path.splitext(file)[0]}_{tool.__name__.lower().replace("tool","")}{normalize_extension(output_type)}'

            w=ToolWorker(file,output,tool,options,config.getint('processing','threads'))
            w.signals.error.connect(self._worker_error_signal)
            w.signals.progress.connect(self._worker_progress_signal)
            w.signals.finished.connect(lambda:self._worker_finished_signal(run_button,cancel_button))
            w.signals.result.connect(self._worker_result_signal)
            w.signals.canceled.connect(self._worker_canceled_signal)
            self.thread_queue.add(w)

        run_button.setDisabled(True)
        cancel_button.setEnabled(True)
        self.ui.tools_list.setDisabled(True)

        

    def cancel_processing(self):
        self.thread_queue.stop(False)
        logger.info('Cancelled processing.')

    #worker signals
    @Slot()
    def _worker_error_signal(self,e:Exception):
        if type(e)==ToolRunException:
            logger.error(e)
        else:
            tb=traceback.format_exception(type(e),e,e.__traceback__)
            logger.error('From worker:\n'+'\n'.join(tb))
    @Slot()
    def _worker_progress_signal(self,percent:int):
        self.ui.progress_bar.setEnabled(True)
        if percent==-1:
            self.ui.progress_bar.setRange(0,0)
        else:
            self.ui.progress_bar.setValue(percent)
    @Slot()
    def _worker_result_signal(self,result:str):
        logger.info(f'Finished {os.path.split(result)[1]}')

    @Slot()
    def _worker_canceled_signal(self,result:str):
        if os.path.exists(result):
            logger.info(f'Deleting {os.path.split(result)[1]}...')
            os.remove(result)
    
    @Slot()
    def _worker_finished_signal(self,run_button,cancel_button):
        n=self.thread_queue.thread_queue.qsize()
        if self.thread_queue.thread_running:n+=1
        self.ui.progress_bar.setValue(0)
        if n==0:
            logger.info(f'All files completed')
            self.ui.progress_bar.setRange(0,100)
            self.ui.progress_bar.setEnabled(False)
            run_button.setEnabled(True)
            cancel_button.setDisabled(True)
            self.ui.tools_list.setEnabled(True)
        else:
            logger.info(f'{n} item{n>1 and "s" or ""} left')
    #misc
    #File info
    def show_file_info(self,file:str):
        info=get_video_info(file)
        html=json2html.convert(json=info)
        self.ui.info_text_edit.setHtml(html)

        file_type=f'{os.path.splitext(file)[1]} {info.get("format",{}).get("format_long_name","N/A")}'
        self.ui.info_type_line.setText(file_type)

        file_length=seconds=info.get('format',{}).get('duration','N/A')
        if file_length!='N/A':
            file_length=humanize.naturaldelta(timedelta(seconds=float(file_length)))
        self.ui.info_length_line.setText(file_length)

        file_size=humanize.naturalsize(os.path.getsize(file),True,False,'%.2f')
        self.ui.info_size_line.setText(file_size)

        file_bitrate=list_get(info.get('streams',[]),0,{}).get('bit_rate','N/A')
        if file_bitrate!='N/A':
            file_bitrate=humanize.naturalsize(float(file_bitrate)*1.024,True,False,'%.2f')+'ps'
        self.ui.info_bitrate_line.setText(file_bitrate)

        file_audio_tracks=len(info.get('streams',[]))-1
        if file_audio_tracks<1:file_audio_tracks='N/A'
        else:
            audio_types=[]
            for stream in info.get('streams')[1:]:
                audio_types.append(stream.get('codec_name','N/A'))
            file_audio_tracks=f'{file_audio_tracks}'+(f' ({",".join(audio_types)})' if audio_types else '')
        self.ui.info_audiotracks_line.setText(file_audio_tracks)

    

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
