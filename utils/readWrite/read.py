import os

def configRead():
    configList = []
    with open('config.txt', 'r') as configFile:
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