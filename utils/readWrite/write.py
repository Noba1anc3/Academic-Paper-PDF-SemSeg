import os
import cv2
import sys
import json

from utils.logging.syslog import Logger

sys.dont_write_bytecode = True

def ImageWrite(ImageList, fileName, fileFolder):
    imgFolder = fileFolder + fileName[:-4] + '/'

    if not os.path.exists(imgFolder[:-1]):
        os.mkdir(imgFolder)

    for index in range(len(ImageList)):
        Image = ImageList[index]
        imgName = fileName[:-4] + '_p' + str(index+1) + '.jpg'
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
    estFile = fileFolder + fileName[:-4] + '.txt'

    Precision_Num = 0
    Recall_Num = 0
    F1_Num = 0
    Precision_Area = 0
    Recall_Area = 0
    F1_Area = 0
    num = 0

    with open(estFile, 'w') as f:
        for key in p_num.keys():
            f.write(key + ':' + '\n')
            f.write('  Precision_Num: ' + "%.2f" % (float(p_num[key])) + '\n')
            f.write('  Recall_Num: ' + str("%.2f" % (float(r_num[key]))) + '\n')
            f.write('  F1_Num: ' + str("%.2f" % (float(f_num[key]))) + '\n')
            f.write('  Precision_Area: ' + str("%.2f" % (float(p_area[key]))) + '\n')
            f.write('  Recall_Area: ' + str("%.2f" % (float(r_area[key]))) + '\n')
            f.write('  F1_Area: ' + str("%.2f" % (float(f_area[key]))) + '\n')

            if fileName == 'AAAAA.pdf':
                if p_num[key] != 'NaN':
                    num += 1
                    Precision_Num += p_num[key]
                    Recall_Num += r_num[key]
                    F1_Num += f_num[key]
                    Precision_Area += p_area[key]
                    Recall_Area += r_area[key]
                    F1_Area += f_area[key]

        if fileName == 'AAAAA.pdf':
            f.write('All_Average' + ':' + '\n')
            f.write('  Precision_Num: ' + str(format(Precision_Num / num, '.2f')) + '\n')
            f.write('  Recall_Num: ' + str(format(Recall_Num / num, '.2f')) + '\n')
            f.write('  F1_Num: ' + str(format(F1_Num / num, '.2f')) + '\n')
            f.write('  Precision_Area: ' + str(format(Precision_Area / num, '.2f')) + '\n')
            f.write('  Recall_Area: ' + str(format(Recall_Area / num, '.2f')) + '\n')
            f.write('  F1_Area: ' + str(format(F1_Area / num, '.2f')) + '\n')

        f.close()