import os
from configparser import ConfigParser
from utils.logging.syslog import Logger

class Configuration():
    def __init__(self):
        logging = Logger(__name__)
        Logger.get_log(logging).info('Start processing ConfigFile')
        self.config()
        Logger.get_log(logging).info('ConfigFile Processed')

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

class annotation():
    def __init__(self):
        self.annotateRead()

    def annotateRead(self):
        pass
