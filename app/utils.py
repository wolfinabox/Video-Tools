from typing import Any
from pyparsing import Word,nums,CaselessLiteral,ParseException
from subprocess import Popen,PIPE,STDOUT,CREATE_NO_WINDOW
from json import loads
import os
import errno

def is_executable()->bool:
    """
    Determine if the current script is packaged as an executable\n
    (EG: If packed into a .exe with PyInstaller)\n
    returns : True/False, if the script is an executable
    """
    import sys
    return getattr(sys,'frozen',False)

def script_dir()->str:
    """
    Get the path to the current script's directory, whether running as an executable or in an interpreter.\n
    returns : A string containing the path to the script directory.
    """
    from os import path
    import sys
    return path.dirname(sys.executable) if is_executable() else os.path.join(path.dirname(path.realpath(sys.argv[0])),'app')

def local_path(dir_name:str='')->str:
    """
    Get the absolute path to a local file/directory __MEIPASS or .), whether running as an executable or in an interpreter.\n
    returns : A string containing the path to the local file/directory
    """
    from os import path
    import sys
    return path.join(sys._MEIPASS, dir_name) if is_executable() else path.join(script_dir(),dir_name)


def convert_size_to_bytes(size_str:str):
    """
    Converts a size string (eg: "12gb") to bytes.
    """
    multipliers={"kb":1024,"mb":1024000,"gb":1024000000,"tb":1024000000000} #god help whoever converts a tb file
    expr=Word(nums+','+'.').setParseAction(lambda toks:float(toks[0])).setResultsName('size')+(CaselessLiteral('kb')^ CaselessLiteral('mb') ^ CaselessLiteral('gb') ^ CaselessLiteral('tb')).setParseAction(lambda toks:multipliers[toks[0]]).setResultsName('mult')
    result=None
    try:
        result=expr.parseString(size_str.replace(',',''))
    except ParseException:
        return None
    return result.size*result.mult

def is_int(s:str):
    """
    Return whether or not the str `s` is an int.
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_video_info(filename:str,ffprobe:str=os.path.join(local_path('resources'),'ffprobe.exe')):
    """
    Get the video info from a video file.\n
    Returns a JSON object
    """
    command = [ffprobe,
            "-loglevel",  "quiet",
            "-print_format", "json",
             "-show_format",
             "-show_streams",
             filename
             ]
    pipe = Popen(command, stdout=PIPE, stderr=STDOUT,creationflags = CREATE_NO_WINDOW)
    out, err = pipe.communicate()
    return loads(out)


def get_free_space_b(dirname):
    """Return folder/drive free space (in bytes)."""
    import ctypes
    import os
    import platform
    import sys
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize


def vid_time_to_ms(time_str:str):
    h,m,s=time_str.split(':')
    s,ms=s.split('.')
    ms=ms.rstrip('0')
    if not ms:ms='0'
    h,m,s,ms=map(float,(h,m,s,ms))
    ms+=(s*1000)
    ms+=(m*60*1000)
    ms+=(h*60*60*1000)
    return ms

class Custom_Zip():
    """Same basic functionality as zip() builtin, but can be used with differently size iterators
    """
    def __init__(self,*args,default:Any=None):
        """Same as zip() builtin, but returns default from any iters that are exhausted until all are exhausted

        Args:
            default (Any, optional): [description]. Defaults to None.
        """
        self.args=[iter(c) for c in args]
        self.default=default

    def __iter__(self):
        return self
    
    def __next__(self):
        yields=[]
        for arg in self.args:
            yields.append(next(arg,self.default))
        if all(c is None for c in yields):
            raise StopIteration
        return tuple(yields)

def make_dirs(path:str):
    """Make the directory path specified.

    Args:
        path (str): The path to create. Should either be a file (eg: /foo/bar/baz.txt), or a directory ending in / (/foo/bar/)
    """
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def normalize_extension(ext:str,dot=True):
    if dot: return '.'+ext.lstrip('.')
    else: return ext.lstrip('.')

class file_str(str):
    """Empty subclass of str builtin, for use with type requiring
    """
    pass

def list_get (l:list, idx:int, default:Any=None):
  try:
    return l[idx]
  except IndexError:
    return default