import os
import sys

from configparser import ConfigParser
from utils.logging.syslog import Logger

sys.dont_write_bytecode = True

class Configuration():
    def __init__(self):
        self.logging = Logger(__name__)
        Logger.get_log(self.logging).info('Start processing ConfigFile')
        self.config()
        Logger.get_log(self.logging).info('ConfigFile Processed\n')

    def config(self):
        cp = ConfigParser()
        cp.read('conf.cfg')
        self.folder = cp.get('configuration', 'folder')
        self.filename = cp.get('configuration', 'filename')
        self.tit_choice = cp.getint('configuration', 'tit_choice')
        self.text_level = cp.getint('configuration', 'text_level')
        self.table_level = cp.getint('configuration', 'table_level')
        self.evaluate = cp.getboolean('configuration', 'evaluate')
        self.save_text = cp.getboolean('configuration', 'save_text')
        self.save_image = cp.getboolean('configuration', 'save_image')

        self.configCheck()

        seg_result_folder = 'example/seg_result/'
        if not os.path.exists(seg_result_folder):
            os.mkdir(seg_result_folder)

        if self.evaluate == True:
            self.eva_folder = seg_result_folder + 'evaluation/'
            if not os.path.exists(self.eva_folder):
                os.mkdir(self.eva_folder)

        if self.save_text == True:
            self.json_folder = seg_result_folder + 'json/'
            if not os.path.exists(self.json_folder):
                os.mkdir(self.json_folder)

        if self.save_image == True:
            self.img_folder = seg_result_folder + 'image/'
            if not os.path.exists(self.img_folder):
                os.mkdir(self.img_folder)

        if self.filename == 'all':
            self.fileList = sorted(os.listdir(self.folder))
        else:
            self.fileList = [self.filename]

    def configCheck(self):
        if not self.folder[-1] == '/':
            Logger.get_log(self.logging).critical('Configuration - Folder Not End With / ')
            y_n = input("Do you want system add '/' to the end of folder ? (Y/N)\n")
            if y_n.lower() == 'y' or y_n.lower() == 'yes':
                self.folder += '/'
            else:
                sys.exit()

        if not self.filename == 'all' and not self.filename[-4:] == '.pdf':
            Logger.get_log(self.logging).critical('Configuration - FileName Not End With .pdf ')
            y_n = input("Do you want system add '.pdf' to the end of filename ? (Y/N)\n")
            if y_n.lower() == 'y' or y_n.lower() == 'yes':
                self.filename += '.pdf'
            else:
                sys.exit()

        if not (self.tit_choice == 0 or self.tit_choice == 1 or self.tit_choice == 2 or self.tit_choice == 3):
            Logger.get_log(self.logging).critical('Configuration - tit_choice Format Error ')
            while True:
                tit_choice = input("Please press 0/1/2/3 to specify a tit_choice \n")
                if tit_choice == '0' or tit_choice == '1' or tit_choice == '2' or tit_choice == '3':
                    self.tit_choice = tit_choice
                    break

        if not (self.text_level == 1 or self.text_level == 2):
            Logger.get_log(self.logging).critical('Configuration - text_level Format Error ')
            while True:
                text_level = input("Please press 1/2 to specify a text_level \n")
                if text_level == '1' or text_level == '2':
                    self.text_level = text_level
                    break

        if not (self.table_level == 1 or self.table_level == 2):
            Logger.get_log(self.logging).critical('Configuration - table_level Format Error ')
            while True:
                table_level = input("Please press 1/2 to specify a table_level \n")
                if table_level == '1' or table_level == '2':
                    self.text_level = table_level
                    break


class annotation():
    def __init__(self):
        self.annotateRead()

    def annotateRead(self):
        pass
