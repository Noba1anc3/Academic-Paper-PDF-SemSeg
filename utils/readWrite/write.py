import os
import cv2
import json
from utils.logging.syslog import Logger

def ImageWrite(ImageList, fileName, fileFolder):
    imgFolder = fileFolder + fileName[:-4] + '/'

    if not os.path.exists(imgFolder[:-1]):
        os.mkdir(imgFolder)

    for index in range(len(ImageList)):
        Image = ImageList[index]
        imgName = fileName[:-4] + '_' + str(index) + '.jpg'
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

def EstimationWrite(pre, rec, f1, fileName, fileFolder):
    estFile = fileFolder + fileName[:-4] + '.txt'

    with open(estFile, 'w') as f:
        f.write('Precision: ' + str(pre) + '\n')
        f.write('Recall: ' + str(rec) + '\n')
        f.write('F1: ' + str(f1) + '\n')