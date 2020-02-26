from utils.readWrite.read import *
from utils.readWrite.write import *

from utils.formatChange.pdf2xml import pdf2layout
from utils.formatChange.pdf2image import pdf2image
from utils.formatChange.result2json import rst2json
from utils.formatChange.result2image import rst2image

from semseg.semseg import *
from estimate.estimation import estimate

from logzero import logger
import sys

if __name__ == '__main__':
    configList, fileFolder, fileList = config()

    for index in range(len(fileList)):
        fileName = fileList[index]

        if not fileName.endswith('.pdf'):
            logger.info('{} is skipped  ({}/{})'.format(fileName, index+1, len(fileList)))
            continue
        else:
            logger.info('Processing File {}  ({}/{})'.format(fileName, index+1, len(fileList)))

        filePath = fileFolder + fileName
        PagesImage  = pdf2image(filePath)
        PagesLayout = pdf2layout(filePath)
        if not PagesLayout == None:
            SemanticSegmentation(PagesImage, PagesLayout, configList)

        if configList[2] == 'True':
            annotateRead()
            estimate()
        else:
            if configList[6] == 'True':
                rst2image()
                ImageWrite()
            if configList[7] == 'True':
                rst2json()
                JsonWrite()

        c = str(input())
        if c == 'q':
            sys.exit()

    logger.info("All file processed")