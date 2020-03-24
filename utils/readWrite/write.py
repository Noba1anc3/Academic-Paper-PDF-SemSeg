import os
import cv2
import sys
import json
import numpy as np
from utils.logging.syslog import Logger

sys.dont_write_bytecode = True


def ImageWrite(ImageList, fileName, fileFolder):
    imgFolder = fileFolder + fileName[:-4] + '/'

    if not os.path.exists(imgFolder[:-1]):
        os.mkdir(imgFolder)

    for index in range(len(ImageList)):
        Image = ImageList[index]
        imgName = fileName[:-4] + '_p' + str(index+1) + '.jpg'
        if isinstance(Image, np.ndarray):
            cv2.imwrite(imgFolder + imgName, Image)

    logging = Logger(__name__)
    Logger.get_log(logging).info('Image Saved')
    logging.logger.handlers.clear()


def JsonWrite(JsonFile, fileName, fileFolder):
    jsonPath = fileFolder + fileName[:-4] + '.json'
    with open(jsonPath, 'w') as f:
        json.dump(JsonFile, f)

    logging = Logger(__name__)
    Logger.get_log(logging).info('JsonFile Saved')
    logging.logger.handlers.clear()


def EstimationWrite(p_num, r_num, f_num, p_area, r_area, f_area, fileName, fileFolder):
    SemType = {'Title': '标题', 'Author': '作者', 'FigureNote': '图注',
               'TableNote': '表注', 'Note': '注释', 'PageNo': '页码',
               'Text': '正文', 'Figure': '图片', 'Table': '表格', 'Cell': '单元格'}

    estFile = fileFolder + fileName[:-4] + '.txt'
    Precision_Num = 0.0
    Recall_Num = 0.0
    F1_Num = 0.0
    Precision_Area = 0.0
    Recall_Area = 0.0
    F1_Area = 0.0
    num = 0
    with open(estFile, 'w') as f:
        f.write('|| 基于个数的准确率 | 基于个数的召回率 | 基于个数的F1 | 基于面积的准确率 | 基于面积的召回率 | 基于面积的F1 |\n')
        f.write('| -------- | -------- | -------- | -------- | -------- | -------- | -------- |\n')
        for key in p_num.keys():
            f.write('|' + SemType[key] + '|' + str(p_num[key]) + '|' + str(r_num[key]) + '|' +
                    str(f_num[key]) + '|' + str(p_area[key]) + '|' + str(r_area[key]) + '|' + str(f_area[key])
                    + '|' + '\n')
            if p_num[key] != 'NaN':
                num += 1
                Precision_Num += p_num[key]
                Recall_Num += r_num[key]
                F1_Num += f_num[key]
                Precision_Area += p_area[key]
                Recall_Area += r_area[key]
                F1_Area += f_area[key]

        if fileName == 'AAAAA':
            f.write('|' + '所有' + '|' + format(Precision_Num / num, '.2f') + '|' + format(Recall_Num / num, '.2f')
                    + '|' + format(F1_Num / num, '.2f') + '|' + format(Precision_Area / num, '.2f') + '|'
                    + format(Recall_Area / num, '.2f') + '|' + format(F1_Area / num, '.2f') + '|' + '\n')

        f.close()
