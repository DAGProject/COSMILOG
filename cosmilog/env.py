# -*- coding: utf-8 -*-
"""
Created on Fri May  3 14:43:58 2019

@author: msh, yk
"""
try:
    import string
except:
    print("Can't import string?")
    exit(0)

try:
    import random
except:
    print("Can't import random?")
    exit(0)

try:
    from numpy import genfromtxt
    from numpy import savetxt
    from numpy import array as ar
except:
    print("Can't import numpy.")
    exit(0)

try:
    from os.path import expanduser
    from os.path import exists
    from os.path import isfile
    from os.path import dirname
    from os.path import basename
    from os.path import realpath
    from os.path import splitext
    from os.path import abspath
    from os import remove
    from os import mkdir
except:
    print("Can't import os?")
    exit(0)

try:
    from glob import glob
except:
    print("Can't import glob?")
    exit(0)

try:
    from shutil import copy2
    from shutil import move
except:
    print("Can't import shutil?")
    exit(0)

try:
    from datetime import datetime
except:
    print("Can't import datetime?")
    exit(0)

try:
    from getpass import getuser
except:
    print("Can't import getpass?")
    exit(0)

try:
    from platform import uname
    from platform import system
except:
    print("Can't import platform?")
    exit(0)

try:
    from inspect import currentframe
    from inspect import getouterframes
except:
    print("Can't import inspect?")
    exit(0)

try:
    import tempfile
except:
    print("Can't import tempfile?")
    exit(0)
    
class Logger():
    def __init__(self, verb=True, debugger=False):
        """Constructor method."""
        self.verb = verb
        self.debugger = debugger
        self.log_dir = abspath("{}/mylog/".format(expanduser("~")))
        self.log_file = abspath("{}/log.my".format(self.log_dir))
        self.mini_log_file = abspath("{}/mlog.my".format(self.log_dir))
        self.tmp_dir = tempfile.gettempdir()
        
        self.setting_file = abspath("{}/.cosmolog.set".format(expanduser("~")))
        self.masks_file = abspath("{}/.cosmolog.msk".format(expanduser("~")))
        
        self.observat_dir = abspath("./observat/")
        
    def random_string(self, length):
        """Returns a random string with given length"""
        return(''.join(random.choices(
                string.ascii_uppercase + string.digits, k=length)))
        
    def time_stamp(self):
        """Return timestamp (UTC) YYYY-mm-ddTHH:MM:SS."""
        return(str(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")))
        
    def time_stamp_(self):
        """Return timestamp (UTC) YYYY-mm-ddTHH-MM-SS."""
        return(str(datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")))
    
    def user_name(self):
        """Returns user name"""
        return(str(getuser()))
    
    def system_info(self):
        """returns system information"""
        si = uname()
        return("{}, {}, {}, {}".format(si[0], si[2], si[5], self.user_name()))
        
    def caller_function(self, pri=False):
        """Returns caller function"""
        curframe = currentframe()
        calframe = getouterframes(curframe, 2)
        caller = calframe
        self.system_info()
        if pri:
            return("{}>{}>{}".format(
                    caller[0][3], caller[1][3], caller[2][3]))
        else:
            return(caller)
            
    def print_if(self, text):
        """Prints the text if verb is True."""
        if self.verb:
            print("[{}|{}] --> {}".format(self.time_stamp(),
                  self.system_info(), text))
            
    def log(self, text):
        """Logs text if debugger is True."""
        try:
            self.print_if(text)
            if self.debugger:
                log_file = open(self.log_file, "a")
                log_file.write("Time: {}\n".format(self.time_stamp()))
                log_file.write("System Info: {}\n".format(self.system_info()))
                log_file.write("Log: {}\n".format(text))
                log_file.write("Function: {}\n\n\n".format(
                        self.caller_function()))
                log_file.close()
                self.mini_log(text)
        except Exception as e:
            print(e)
        
    def mini_log(self, text):
        """Writes mini log file"""
        mini_log_file = open(self.mini_log_file, "a")
        mini_log_file.write("[{}|{}] --> {}\n".format(self.time_stamp(),
                            self.system_info(), text))
        mini_log_file.close()
        
    def dump_mlog(self):
        """Deletes mini log file"""
        try:
            self.log("Deleting the Mini Log file.")
            mini_log_file = open(self.mini_log_file, "w")
            mini_log_file.close()
        except Exception as e:
            print(e)
        
    def dump_log(self):
        """Deletes log file"""
        try:
            self.log("Deleting the Log file.")
            log_file = open(self.log_file, "w")
            log_file.close()
        except Exception as e:
            print(e)
        
    def is_it_windows(self):
        """Returns True if system is windows"""
        self.log("Checking if the OS is Windows")
        return(system() == 'Windows')
        
    def is_it_linux(self):
        """Returns True if system is linux"""
        self.log("Checking if the OS is Linux")
        return(system() == 'Linux')
        
    def is_it_other(self):
        """Returns True if system is other"""
        self.log("Checking if the OS is Other")
        return(not (self.is_it_linux() or self.is_it_windows()))
        
    def beep(self):
        """Plays a beep"""
        print("\a")
        
class File():
    def __init__(self, verb=False, debugger=False):
        """Constructor method."""
        self.verb = verb
        self.debugger = debugger
        self.logger = Logger(verb=self.verb, debugger=self.debugger)
        
    def abs_path(self, path):
        """Returns Absolute path"""
        try:
            return(abspath(path))
        except Exception as e:
            self.logger.log(e)
            

    def list_of_fiels(self, path, ext="*"):
        """Returns list of files"""
        try:
            if self.is_dir(path):
                pt = self.abs_path("{}/{}".format(path, ext))
                return(sorted(glob(pt)))
        except Exception as e:
            self.logger.log(e)  
            
    def is_file(self, src):
        """Returns True if file is available"""
        self.logger.log("Checking if file {0} exist".format(src))
        try:
            return(isfile(src))
        except Exception as e:
            self.logger.log(e)
            return(False)
    def is_dir(self, src):
        """Returns True if direcoty is available"""
        self.logger.log("Checking if directory {0} exist".format(src))
        try:
            return((not self.is_file(src)) and exists(src))
        except Exception as e:
            self.logger.log(e)
            return(False)
    
    def get_home_dir(self):
        """Returns home directorys path"""
        self.logger.log("Getting Home dir path")
        try:
            return(expanduser("~"))
        except Exception as e:
            self.logger.log(e)
    
    def get_base_name(self, src):
        """Returns path and file name of given absolute path"""
        self.logger.log("Finding path and file name for {0}".format(src))
        try:
            pn = dirname(realpath(src))
            fn = basename(realpath(src))
            return(pn, fn)
        except Exception as e:
            self.logger.log(e)
    
    def get_extension(self, src):
        """Returns extension of a given file"""
        self.logger.log("Finding extension for {0}".format(src))
        try:
            return(splitext(src))
        except Exception as e:
            self.logger.log(e)
            
    def split_file_name(self, src):
        """Returns path, file name and extension of given absolute path"""
        self.logger.log("Chopping path {0}".format(src))
        try:
            path, name = self.get_base_name(src)
            name, extension = self.get_extension(name)
            return(path, name, extension)
        except Exception as e:
            self.logger.log(e)
            
    def cp(self, src, dst):
        """Copys a file to a destination"""
        self.logger.log("Copying file {0} to {1}".format(src, dst))
        try:
            copy2(src, dst)
        except Exception as e:
            self.logger.log(e)
            
    def rm(self, src):
        """Removes a file"""
        self.logger.log("Removing file {0}".format(src))
        try:
            remove(src)
        except Exception as e:
            self.logger.log(e)
            
    def mv(self, src, dst):
        """Moves a file to a destination/Rename"""
        self.logger.log("Moving file {0} to {1}".format(src, dst))
        try:
            move(src, dst)
        except Exception as e:
            self.logger.log(e)
            
    def mkdir(self, path):
        """Creates a directory"""
        try:
            if not self.is_dir:
                mkdir(path)
        except Exception as e:
            self.logger.log(e)
            
    def read_array(self, src, dm=" ", dtype=float):
        """Reads an ascii file to a numpy array"""
        self.logger.log("Reading {0}".format(src))
        try:
            return(genfromtxt(src, comments='#', delimiter=dm, dtype=dtype))
        except Exception as e:
            self.logger.log(e)
            
    def write_array(self, src, arr, dm=" ", h=""):
        """Writes a numpy array to an ascii file"""
        self.logger.log("Writing to {0}".format(src))
        try:
            arr = ar(arr)
            savetxt(src, arr, delimiter=dm, newline='\n', header=h)
        except Exception as e:
            self.logger.log(e)