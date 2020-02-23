from utils.readWrite.read import configRead
from utils.formatChange.pdfminer import layout_analysis
from utils.formatChange.pdf2image import pdf2image
from semseg.semseg import *
from logzero import logger
import sys

if __name__ == '__main__':
    configList, fileFolder, fileList = configRead()

    for index in range(len(fileList)):
        fileName = fileList[index]

        if not fileName.endswith('.pdf'):
            logger.info('{} is skipped  ({}/{})'.format(fileName, index+1, len(fileList)))
            continue
        else:
            logger.info('Processing File {}  ({}/{})'.format(fileName, index+1, len(fileList)))

        filePath = fileFolder + fileName
        PagesLayout = layout_analysis(filePath)
        PagesImage  = pdf2image(filePath)

        Segmentation(PagesImage, PagesLayout)

        if configList[2] == 'True':
            c = str(input())
            if c == 'q':
                sys.exit()

    logger.info("All file processed")