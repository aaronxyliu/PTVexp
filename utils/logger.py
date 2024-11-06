import inspect
import os
import datetime
import re
import sys


class getLogger:
    # Static variable
    # Ensure the uniqueness of the logger
    global_logger = None

    def __init__(self):
        if getLogger.global_logger:
            return getLogger.global_logger
        
        self.indent_num = 0
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
        self.__write_to_file__(f'$> {' '.join(sys.argv)}\n')

        getLogger.global_logger = self
        
        print(f'A new log file is created at: {self.filepath}')

    def close(self):
        pass
    
    def indent(self):
        self.indent_num += 1

    def outdent(self):
        if self.indent_num > 0:
            self.indent_num -= 1
    
    def __write_to_file__(self, content: str):
        outfile = open(self.filepath, "a")
        outfile.write(content)
        outfile.close()

    def info(self, content=''):
        time_str = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        header = '[INFO]'
        indent = ' ' * self.indent_num * 2
        print(colors.fg.green, time_str, colors.fg.green, header, colors.reset, indent, content)
        self.__write_to_file__(f'{time_str} {header} {indent}{str(content)}\n')
    
    def debug(self, content=''):
        outfile = open(self.filepath, "a")
        time_str = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        header = '[DEBUG]'
        print(colors.fg.green, time_str, colors.fg.blue, header, colors.reset, content)
        self.__write_to_file__(f'{time_str} {header} {str(content)}\n')
    
    def warning(self, content=''):
        time_str = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        header = '[WARNING]'
        print(colors.fg.green, time_str,  colors.fg.orange, header, colors.reset, content)
        self.__write_to_file__(f'{time_str} {header} {str(content)}\n')
    
    def error(self, content=''):
        time_str = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        header = '[ERROR]'
        print(colors.fg.green, time_str,  colors.fg.red, header, colors.reset, content)
        self.__write_to_file__(f'{time_str} {header} {str(content)}\n')
    
    def newline(self):
        print('')
        self.__write_to_file__(f'\n')

    def custom(self, title, content=''):
        # The title text is defined by user
        time_str = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        header = f'[{str(title).upper()}]'
        print(colors.fg.green, time_str, colors.fg.green, header, colors.reset, content)
        self.__write_to_file__(f'{time_str} {header} {str(content)}\n')





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
