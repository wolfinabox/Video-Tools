import os
from subprocess import Popen,PIPE,STDOUT
import humanize
import subprocess
from app.utils import file_str, get_video_info, local_path,get_free_space_b,vid_time_to_ms,list_get
import daiquiri
logger=daiquiri.getLogger('workflow-tool')

class ToolRunException(Exception):
    pass

BASE_FFMPEG_COMMAND='"{0}" -y -v error -stats -threads {2} -i "{1}" '
FFMPEG_PATH=os.path.join(local_path('resources'),'ffmpeg.exe')


class BaseTool():
    """Base class for tools
    """
    description="Default tool description"
    required_options=[]
    allowed_inputs,allowed_outputs=[],[]
    ffmpeg_command:str=BASE_FFMPEG_COMMAND
    single_file=False
    def __init__(self):
        self.percent_complete=0.0
        self.process:subprocess.Popen=None

    def check_file(self,file:str,filetypes:list=None,try_ignore_errors:bool=False,real_file=True):
        """Check the given file is valid for this tool

        Args:
            file (str): The file path to check

        Raises:
            FileNotFoundError: File doesn't exist
            ToolRunException: File is of incorrect type
            try_ignore_errors (bool,optional): Try to process the file, ignoring all errors. May or may not work
            real_file (bool,optional): Whether or not the file is real, or just a path/name
        """
        if not filetypes:filetypes=self.allowed_inputs
        if real_file:
            if not os.path.exists(file):
                raise FileNotFoundError(f'File {file} does not exist')
        if not filetypes:return
        filetype = os.path.splitext(file)[1][1:]
        if filetype not in filetypes:
            if not try_ignore_errors: raise ToolRunException(f'Invalid file type {filetype}. Must be {str(filetypes)} ')
            else: logger.warn(f'Invalid file type {filetype}. Trying to ignore...')

    def check_space_available(self,new_size:int,dir:str):
        """Check if there is enough space in the given directory for the given size

        Args:
            new_size (int): The size required in bytes
            dir (str): The directory to check the remaining space of`

        Returns:
            bool: True/false depending if there's enough space
        """
        remaining_space_b=get_free_space_b(dir)
        if remaining_space_b<=new_size:
            return False
        return True

    def check_options(self,options:dict):
        """Check the options provided against the required options for this tool

        Args:
            options (dict): The user provided options

        Raises:
            ToolRunException: The reason the given options are invalid
        """
        if not options:
            raise ToolRunException('Options required but not provided. Required options: '+', '.join(f"{option[0]}:{option[1]}" for option in self.required_options))
        for option in self.required_options:
            if option[0] not in options:
                    raise ToolRunException(f'Option "{option[0]}" with type {option[1]} required but not provided')
            #single type
            if type(option[1])==type(type):
                if not issubclass(option[1],type(options[option[0]])):
                    raise ToolRunException(f'Option "{option[0]}" should be of type "{option[1]}", got {type(options[option[0]])}')
            #tuple/list of options
            else:
                if options[option[0]] not in option[1]:
                    raise ToolRunException(f'Option {option[0]} must be one of {option[1]}')

    def run(self,file:str,output_file:str=None,options:dict=None,threads:int=1,try_ignore_errors:bool=False)->str: 
        """Run the tool on the given file

        Args:
            file (str): The file to process
            output_file (str): The file name to output to. Defaults to None (same dir as input)
            options (dict, optional): The options to run the tool with. Defaults to None.
            threads (int, optional): The amount of threads to use. Defaults to 1.
            try_ignore_errors (bool,optional): Try to process the file, ignoring all errors. May or may not work, and some errors are not ignorable

        Returns:
            str: The path to the output file
        """
        raise NotImplementedError
    
    def stop(self):
        self.process.kill()

    def _run_process(self,process:subprocess.Popen,file_shortname:str,total_vid_ms:int):
        """Generic FFMpeg output processor

        Args:
            process (subprocess.Popen): The running ffmpeg process
            file_shortname (str): The file's name
            total_vid_ms (int): The length of the video in ms

        Raises:
            ToolRunException: Raised if the ffmpeg process failed
        """
        can_percent=(self.percent_complete!=-1)
        err_lines=[]
        for out in process.stdout:
            out=out.strip() if isinstance(out,str) else out
            if out:
                logger.debug(out)
                #parse output
                tag=None
                if any(t in out for t in ('[error]','Error')):tag='error'
                elif '[fatal]' in out:tag='fatal'
                else: tag='info'
               
                #good output, process time n stuff
                if tag=='info':
                    if total_vid_ms:
                        try:
                            line_parts=out.split()
                            time=[l for l in line_parts if 'time=' in l][0].split('=')[1]
                            time_ms=vid_time_to_ms(time)
                            if can_percent:
                                self.percent_complete=round(time_ms/total_vid_ms*100.0,2)
                                if self.percent_complete>100:self.percent_complete=100
                                if self.percent_complete<0:self.percent_complete=0

                            self.percent_callback(self.percent_complete)
                            self.output_callback(out)
                        except IndexError:
                            continue
                #bad output
                elif tag=='error':
                    self.output_callback(out)
                    err_lines.append(out)
                elif tag=='fatal':
                    self.output_callback(out)
                    err_lines.append(out)
                

        if err_lines:
            raise ToolRunException(f'FFmpeg error in file {file_shortname}',err_lines)
        if can_percent and self.percent_complete!=100.00:
            self.percent_complete=100.0
            self.percent_callback(self.percent_complete)

    def percent_callback(self,percent:float):
        """Callback function to be replaced. Is passed the percent of completion every update

        Args:
            percent (float): The percent complete
        """
        ...

    def output_callback(self,output:str):
        """Callback function to be replaced. Is passed the output of the command every update

        Args:
            output (str): The output of the command
        """
        ...


class CustomTool(BaseTool):
    description="Run a custom FFmpeg command"
    required_options=[('Command',str)]
    ffmpeg_command=BASE_FFMPEG_COMMAND+'{4} {3}'
    def __init__(self):
        super().__init__()
    def run(self,file:str,output_file:str,options:dict=None,threads:int=1,try_ignore_errors:bool=False)->str:
        self.percent_complete=-1
        file_shortname=os.path.split(file)[1]

        if not os.path.dirname(output_file):
            output_file=os.path.join(os.path.dirname(file),output_file)
        #check file
        self.check_file(file,self.allowed_inputs,try_ignore_errors)
        self.check_options(options)
        comm=self.ffmpeg_command.format(FFMPEG_PATH,file,threads,output_file,options['Command'])
        readable_command=self.ffmpeg_command.format(os.path.split(FFMPEG_PATH)[1],os.path.split(file)[1],threads,os.path.split(output_file),options['Command'])
        logger.info(f'Running: {readable_command}')
        
        self.process:subprocess.Popen=Popen(comm,stdout=PIPE,stderr=STDOUT,bufsize=1,universal_newlines=True,creationflags = subprocess.CREATE_NO_WINDOW)
        self._run_process(self.process,file_shortname,None)
        return output_file


class ConvertVideoTool(BaseTool):
    """Convert between multiple video types. FLV does NOT support multiple audio tracks
    """
    description="Convert between multiple video types."
    allowed_outputs=allowed_inputs=['mp4','mov','m4v','mkv','flv']
    ffmpeg_command=BASE_FFMPEG_COMMAND+'-map 0:v? -map 0:a? -codec copy "{3}"'
    def __init__(self):
        super().__init__()

    def run(self,file:str,output_file:str,options:dict=None,threads:int=1,try_ignore_errors:bool=False)->str:
        file_shortname=os.path.split(file)[1]
        
        if not os.path.dirname(output_file):
            output_file=os.path.join(os.path.dirname(file),output_file)

        #check file 
        self.check_file(file,self.allowed_inputs,try_ignore_errors)
        self.check_file(output_file,self.allowed_outputs,try_ignore_errors,False)
        if not self.check_space_available(os.path.getsize(file),os.path.dirname(output_file)):
            if not try_ignore_errors: raise ToolRunException(f'Not enough space on drive {os.path.splitdrive(file)[0]} ({humanize.naturalsize(os.path.getsize(file))} required, has {humanize.naturalsize(get_free_space_b(os.path.dirname(output_file)))})')
            else: logger.warn(f'Not enough space on drive {os.path.splitdrive(file)[0]}. Trying to ignore...')
    
        vid_info=get_video_info(file)
        try:
            total_vid_ms=float(vid_info['streams'][0]['duration'])*1000 if 'duration' in vid_info['streams'][0] else vid_time_to_ms(vid_info['streams'][0]['tags']['DURATION'])
        except KeyError as e:
            if not try_ignore_errors: raise ToolRunException(f'File {file_shortname} does not have attribute {e.args[0]}')
            else: 
                logger.warn(f'File {file_shortname} does not have attribute {e.args[0]}. Trying to ignore...')
                total_vid_ms=None


        if file==output_file:
            logger.info(f'{file_shortname} converting to same name, ignoring...')
            self.percent_complete=100.0
            self.percent_callback(self.percent_complete)
            return output_file

            
        comm=self.ffmpeg_command.format(FFMPEG_PATH,file,threads,output_file)
        readable_command=self.ffmpeg_command.format(os.path.split(FFMPEG_PATH)[1],os.path.split(file)[1],threads,os.path.split(output_file)[1])
        #check for multiple audio tracks in unsupported formats (flv)
        if os.path.splitext(output_file)[1][1:] in ('flv',):
            comm=comm.replace('-map 0:v? -map 0:a?','')
            if len(vid_info['streams'])>2: 
                logger.warn(f'{os.path.splitext(output_file)[1][1:].upper()} files do not support multiple audio tracks. Only the first audio track in {file_shortname} will be copied.')
        logger.info(f'Running: {readable_command}')
        
        self.process:subprocess.Popen=Popen(comm,stdout=PIPE,stderr=STDOUT,bufsize=1,universal_newlines=True,creationflags = subprocess.CREATE_NO_WINDOW)
        self._run_process(self.process,file_shortname,total_vid_ms)
        return output_file
        

class ExtractAudioTool(BaseTool):
    """Extract an audio track from a video
    """
    description="Extract an audio track from a video"
    required_options=[('Track Number',int)]
    allowed_inputs=['mp4','mov','m4v','mkv','flv']
    allowed_outputs=['wav','mp3','aiff']
    ffmpeg_command=BASE_FFMPEG_COMMAND+'-map 0:a:{4}? "{3}"'
    def __init__(self):
        super().__init__()

    def run(self,file:str,output_file:str,options:dict=None,threads:int=1,try_ignore_errors:bool=False)->str:
        file_shortname=os.path.split(file)[1]

        if not os.path.dirname(output_file):
            output_file=os.path.join(os.path.dirname(file),output_file)
        #check file
        self.check_file(file,self.allowed_inputs,try_ignore_errors)
        self.check_file(output_file,self.allowed_outputs,try_ignore_errors,False)
        self.check_options(options)
        #no file size to check (can't calculate)

        vid_info=get_video_info(file)
        # json.dump(vid_info,open('test_vid_info.json','w'),indent=3)
        try:
            total_vid_ms=float(vid_info['streams'][0]['duration'])*1000 if 'duration' in vid_info['streams'][0] else vid_time_to_ms(vid_info['streams'][0]['tags']['DURATION'])
        except KeyError as e:
            if not try_ignore_errors: raise ToolRunException(f'File {file_shortname} does not have attribute {e.args[0]}')
            else: 
                logger.warn(f'File "{file_shortname}"" does not have attribute {e.args[0]}. Trying to ignore...')
                total_vid_ms=None
        track_num=options['Track Number']
        if track_num>len(vid_info['streams'])-2:
            raise ToolRunException(f'Track #{track_num} does not exist in file "{file_shortname}"')
        
        comm=self.ffmpeg_command.format(FFMPEG_PATH,file,threads,output_file,track_num)
        readable_command=self.ffmpeg_command.format(os.path.split(FFMPEG_PATH)[1],os.path.split(file)[1],threads,os.path.split(output_file)[1],track_num)
        
        logger.info(f'Running: {readable_command}')
        
        self.process:subprocess.Popen=Popen(comm,stdout=PIPE,stderr=STDOUT,bufsize=1,universal_newlines=True,creationflags = subprocess.CREATE_NO_WINDOW)
        self._run_process(self.process,file_shortname,total_vid_ms)
        return output_file




class AudioInsertTool(BaseTool):
    """Insert an audio track into a video. Replaces audio if track number exists, otherwise inserts a new track
    """
    description="Insert/replace an audio track in a video"
    required_options=[('Track Number',int),('Video File',file_str)]
    allowed_inputs=[('mp3','wav','aiff'),('mp4','mov','m4v','mkv','flv')]
    allowed_outputs=allowed_inputs[1]
    single_file=True
    def __init__(self):
        super().__init__()

    def run(self,file:str,output_file:str,options:dict=None,threads:int=1,try_ignore_errors:bool=False)->str:
        file_shortname=os.path.split(file)[1]
        self.check_options(options)
        track_num=options['Track Number']
        video_file=options['Video File']
        video_file_shortname=os.path.split(video_file)[1]
        if not os.path.dirname(output_file):
            output_file=os.path.join(os.path.dirname(file),output_file)
        #Check files
        self.check_file(file,self.allowed_inputs[0],try_ignore_errors)
        self.check_file(video_file,self.allowed_inputs[1],try_ignore_errors)
        self.check_file(output_file,self.allowed_outputs,real_file=False)
        if not self.check_space_available(os.path.getsize(video_file),os.path.dirname(output_file)):
            if not try_ignore_errors: raise ToolRunException(f'Not enough space on drive {os.path.splitdrive(video_file)[0]} ({humanize.naturalsize(os.path.getsize(video_file))} required, has {humanize.naturalsize(get_free_space_b(os.path.dirname(output_file)))})')
            else: logger.warn(f'Not enough space on drive {os.path.splitdrive(video_file)[0]}. Trying to ignore...')

        vid_info=get_video_info(video_file)
        try:
            total_vid_ms=float(vid_info['streams'][0]['duration'])*1000 if 'duration' in vid_info['streams'][0] else vid_time_to_ms(vid_info['streams'][0]['tags']['DURATION'])
        except KeyError as e:
            if not try_ignore_errors: raise ToolRunException(f'File {video_file_shortname} does not have attribute {e.args[0]}')
            else: 
                logger.warn(f'File {video_file_shortname} does not have attribute {e.args[0]}. Trying to ignore...')
                total_vid_ms=None

        #check for multiple audio tracks in unsupported formats (flv)
        if os.path.splitext(video_file_shortname)[1][1:] in ('flv',):
            if track_num>1:
                raise ToolRunException(f'{os.path.splitext(video_file_shortname)[1][1:].upper()} files do not support multiple audio tracks')
                
        #formulate command
        #add track
        if track_num>len(vid_info['streams'])-2:
            self.ffmpeg_command=BASE_FFMPEG_COMMAND+'-i "{5}" -map 0? -map 1:a? -c:v copy -shortest "{3}"'
        #replace track
        else:
            self.ffmpeg_command=BASE_FFMPEG_COMMAND+'-i "{5}" -map 0? -map -0:a:{4}? -map 1:a? -c:v copy -shortest "{3}"'
        # if os.path.splitext(video_file)[1]!=os.path.splitext(output_file)[1]:
        #     self.ffmpeg_command.replace('-c:v','-c')
        comm=self.ffmpeg_command.format(FFMPEG_PATH,video_file,threads,output_file,track_num,file)
        readable_command=self.ffmpeg_command.format(os.path.split(FFMPEG_PATH)[1],os.path.split(video_file)[1],threads,os.path.split(output_file)[1],track_num,os.path.split(file)[1])

        logger.info(f'Running: {readable_command}')
        
        self.process:subprocess.Popen=Popen(comm,stdout=PIPE,stderr=STDOUT,bufsize=1,universal_newlines=True,creationflags = subprocess.CREATE_NO_WINDOW)
        self._run_process(self.process,video_file_shortname,total_vid_ms)
        return output_file


class CRFCompressTool(BaseTool):
    description="CRF Compress a video."
    allowed_outputs=allowed_inputs=['mp4','mov','m4v','mkv','flv']
    required_options=(('CRF Value',int),('Codec',('x264','x265')))
    ffmpeg_command=BASE_FFMPEG_COMMAND+'-map 0:v? -map 0:a? -vcodec lib{5} -crf {4} "{3}"'
    def __init__(self):
        super().__init__()

    def run(self,file:str,output_file:str,options:dict=None,threads:int=1,try_ignore_errors:bool=False)->str:
        file_shortname=os.path.split(file)[1]

        if not os.path.dirname(output_file):
            output_file=os.path.join(os.path.dirname(file),output_file)
        #check file
        self.check_file(file,self.allowed_inputs,try_ignore_errors)
        self.check_file(output_file,self.allowed_outputs,try_ignore_errors,False)
        self.check_options(options)

        #check space
        # if not self.check_space_available(os.path.getsize(file),os.path.dirname(output_file)):
        #     if not try_ignore_errors: raise ToolRunException(f'Not enough space on drive {os.path.splitdrive(file)[0]} ({humanize.naturalsize(os.path.getsize(file))} required, has {humanize.naturalsize(get_free_space_b(os.path.dirname(output_file)))})')
        #     else: logger.warn(f'Not enough space on drive {os.path.splitdrive(file)[0]}. Trying to ignore...')

        vid_info=get_video_info(file)
        # json.dump(vid_info,open('test_vid_info.json','w'),indent=3)
        try:
            total_vid_ms=float(vid_info['streams'][0]['duration'])*1000 if 'duration' in vid_info['streams'][0] else vid_time_to_ms(vid_info['streams'][0]['tags']['DURATION'])
        except KeyError as e:
            if not try_ignore_errors: raise ToolRunException(f'File {file_shortname} does not have attribute {e.args[0]}')
            else: 
                logger.warn(f'File {file_shortname} does not have attribute {e.args[0]}. Trying to ignore...')
                total_vid_ms=None

        if options['Codec']=='x265' and threads>16:threads=16
        comm=self.ffmpeg_command.format(FFMPEG_PATH,file,threads,output_file,options['CRF Value'],options['Codec'])
        readable_comm=self.ffmpeg_command.format(os.path.split(FFMPEG_PATH)[1],os.path.split(file)[1],threads,os.path.split(output_file)[1],options['CRF Value'],options['Codec'])
        #check if flv so can't output multiple audio tracks
        if os.path.splitext(output_file)[1][1:] in ('flv',):
            comm=comm.replace('-map 0:v? -map 0:a?','')
            if len(vid_info['streams'])>2: 
                logger.warn(f'{os.path.splitext(output_file)[1][1:].upper()} files do not support multiple audio tracks. Only the first audio track in {file_shortname} will be copied.')

        
        logger.info(f'Running: {readable_comm}')

        self.process:subprocess.Popen=Popen(comm,stdout=PIPE,stderr=STDOUT,bufsize=1,universal_newlines=True,creationflags = subprocess.CREATE_NO_WINDOW)
        self._run_process(self.process,file_shortname,total_vid_ms)
        return output_file
    
#TODO
class RemoveAudioTool(BaseTool):
    description="Remove an audio track (or all audio tracks) from a video"

TOOLS=[('Convert Video',ConvertVideoTool),('Extract Audio',ExtractAudioTool),('Insert Audio',AudioInsertTool),('CRF Compress',CRFCompressTool),('Custom Command',CustomTool)]