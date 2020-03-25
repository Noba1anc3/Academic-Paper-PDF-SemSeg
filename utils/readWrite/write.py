import os
import cv2
import json
import numpy as np
from utils.logging.syslog import Logger

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

            f.write('|' + SemType[key] + '|' + f2p(p_num[key]) + '|' +
                    f2p(r_num[key]) + '|' + f1(f_num[key]) + '|' +
                    f2p(p_area[key]) + '|' + f2p(r_area[key]) + '|' +
                    f1(f_area[key]) + '|' + '\n')

            if p_num[key] != 'NaN':
                num += 1
                Precision_Num += p_num[key]
                Recall_Num += r_num[key]
                F1_Num += f_num[key]
                Precision_Area += p_area[key]
                Recall_Area += r_area[key]
                F1_Area += f_area[key]

        if fileName == 'Average.pdf':
            f.write('|' + '所有' + '|' + f2p(Precision_Num / num) +
                    '|' + f2p(Recall_Num / num) + '|' + f1(F1_Num / num) +
                    '|' + f2p(Precision_Area / num) +
                    '|' + f2p(Recall_Area / num) + '|' + f1(F1_Area / num) +
                    '|' + '\n')

        f.close()

def f2p(num):
    if not isinstance(num, str):
        num *= 100
        num = format(num, '.2f') + '%'
    return num

def f1(num):
    if not isinstance(num, str):
        num = format(num, '.2f')
    return num