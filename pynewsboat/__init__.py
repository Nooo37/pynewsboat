from sys import platform        
from .newsboat import Newsboat

# check if system is runnning linux
if platform not in ['linux', 'linux2']:
    raise OSError('Other operating systems than linux are currently not supported.')

