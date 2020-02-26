import os
from configparser import ConfigParser

def config():
    cp = ConfigParser()
    cp.read('conf.cfg')
    folder = cp.get('configuration', 'folder')
    filename = cp.get('configuration', 'filename')
    evaluate = cp.getboolean('configuration', 'evaluate')
    text_level = cp.getint('configuration', 'text_level')
    table_level = cp.getint('configuration', 'table_level')
    tit_choice = cp.getint('configuration', 'tit_choice')
    save_image = cp.getboolean('configuration', 'save_image')
    save_text = cp.getboolean('configuration', 'save_text')

    configList = [folder, filename, evaluate, text_level, table_level, tit_choice, save_image, save_text]

    if save_image == True or save_text == True:
        seg_result_folder = 'example/seg_result/'
        if not os.path.exists(seg_result_folder):
            os.mkdir(seg_result_folder)
        if save_image == True and not os.path.exists(seg_result_folder + 'image/'):
            os.mkdir(seg_result_folder + 'image/')
        if save_text == True and not os.path.exists(seg_result_folder + 'text/'):
            os.mkdir(seg_result_folder + 'text/')

    if evaluate == True:
        fileFolder = folder
    else:
        fileFolder = 'example/pdf_file/'

    if filename == '':
        fileList = sorted(os.listdir(fileFolder))
    else:
        fileList = [filename]

    return configList, fileFolder, fileList

def configRead():
    configList = []
    with open('conf.cfg', 'r') as configFile:
        config = configFile.readlines()
        for index in range(0, len(config), 3):
            cfg = config[index]
            cfgValue = cfg.replace(' ', '').split(":")[1].split('\n')[0]
            configList.append(cfgValue)

    if configList[6] == 'True' or configList[7] == 'True':
        seg_result_folder = 'example/seg_result/'
        if not os.path.exists(seg_result_folder):
            os.mkdir(seg_result_folder)
        if configList[6] == 'True' and not os.path.exists(seg_result_folder + 'image/'):
            os.mkdir(seg_result_folder + 'image/')
        if configList[7] == 'True' and not os.path.exists(seg_result_folder + 'text/'):
            os.mkdir(seg_result_folder + 'text/')

    if configList[2] == 'True':
        fileFolder = configList[0]
    else:
        fileFolder = 'example/pdf_file/'

    if configList[1] == '':
        fileList = sorted(os.listdir(fileFolder))
    else:
        fileList = [configList[1]]

    return configList, fileFolder, fileList

def annotateRead():
    pass
