import inspect
import os
import datetime
import re
import sys
import time


class getLogger:
    # Static variable
    # Ensure the uniqueness of the logger
    global_logger = None

    def __init__(self):
        if getLogger.global_logger:
            return getLogger.global_logger
        
        self.indent_num = 0

        # Used by the left time estimator
        self.enable_lefttime_indicator = False
        self.lefttime = -1
        self.timelist = []  # A queue storing the end time of last several tasks

        caller_filename_full = inspect.stack()[1].filename 
        caller_filename_only = os.path.splitext(os.path.basename(caller_filename_full))[0]

        dir_path = os.path.dirname(os.path.realpath(__file__))
        logpath = os.path.abspath(f'{dir_path}/../log')
        logfiles = os.listdir(logpath)
        index_set = set()
        for filename in logfiles:
            indexpat = re.compile(fr'^{caller_filename_only}\.(\d+)\.log$')
            m = indexpat.match(filename)
            if m:
                index_set.add(int(m.group(1)))
        
        index = 1
        while True:
            if index not in index_set:
                logfile_name = f'{caller_filename_only}.{index}.log'
                break
            index += 1
        
        self.filepath = os.path.join(logpath, logfile_name)
        outfile = open(self.filepath, "a")
        outfile.write(f"$> {' '.join(sys.argv)}\n")
        outfile.close()

        getLogger.global_logger = self
        
        self.info(f'A new log file is created at: {self.filepath}')

    def close(self):
        pass

    def __print__(self, headercolor, header:str, content:str):
        print(' ' * 100, end='\r')   # Ensure covering the previous left time print

        time_str = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        indent = ' ' * self.indent_num * 2
        print(colors.fg.green, time_str, headercolor, header, colors.reset, indent, content)

        if self.enable_lefttime_indicator:
            lefttime_str = 'N/A'
            if self.lefttime >= 0:
                lefttime_str = self.__convert_time_format__(self.lefttime)
            print(colors.fg.cyan, f'<<<< ESTIMATED LEFT TIME: {lefttime_str}  >>>>', colors.reset, end="\r")

    def indent(self):
        self.indent_num += 1

    def outdent(self):
        if self.indent_num > 0:
            self.indent_num -= 1
    
    def __write_to_file__(self, header: str, content):
        time_str = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        indent = ' ' * self.indent_num * 2
        outfile = open(self.filepath, "a")
        outfile.write(f'{time_str} {header} {indent}{str(content)}\n')
        outfile.close()

    def info(self, content=''):
        header = '[INFO]'
        self.__print__(colors.fg.green, header, content)
        self.__write_to_file__(header, content)
    
    def debug(self, content=''):
        header = '[DEBUG]'
        self.__print__(colors.fg.blue, header, content) 
        self.__write_to_file__(header, content)
    
    def warning(self, content=''):
        header = '[WARNING]'
        self.__print__(colors.fg.orange, header, content) 
        self.__write_to_file__(header, content)
    
    def error(self, content=''):
        header = '[ERROR]'
        self.__print__(colors.fg.red, header, content) 
        self.__write_to_file__(header, content)
    
    def newline(self):
        self.__print__(colors.fg.reset, '', '')
        self.__write_to_file__('', '\n')

    def custom(self, title, content=''):
        # The title text is defined by user
        header = f'[{str(title).upper()}]'
        self.__print__(colors.fg.green, header, content)
        self.__write_to_file__(header, content)
    
    def leftTimeEstimator(self, left_no:int):
        # Used to show estimated time to complete the program
        # <left_no>: left number of tasks (assume that every single task will invoke this function)
        
        self.enable_lefttime_indicator = True
        
        now = time.time()
        self.timelist.append(now)
        if len(self.timelist) > 20:     # Track lastest 20 tasks
            self.timelist.pop(0)
        if len(self.timelist) > 1:
            speed = (now - self.timelist[0]) / (len(self.timelist) - 1)
            self.lefttime = int(speed * left_no)
            if self.lefttime < 0:
                self.lefttime = 0
    
    def __convert_time_format__(self, sec):
        sec = sec % (24 * 3600)
        hour = sec // 3600
        sec %= 3600
        min = sec // 60
        sec %= 60
        return "%02d:%02d:%02d" % (hour, min, sec) 



class colors:
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class fg:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        lightred = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'

    class bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        lightgrey = '\033[47m'
