from utils.readWrite.read import *
from utils.readWrite.write import *

from semseg.semseg import *
from estimate.estimation import estimate

from utils.formatChange.pdf2xml import pdf2layout
from utils.formatChange.pdf2image import pdf2image
from utils.formatChange.result2json import rst2json
from utils.formatChange.result2image import rst2image

from logzero import logger

if __name__ == '__main__':
    conf = Configuration()

    for index in range(len(conf.fileList)):
        fileName = conf.fileList[index]

        if not fileName.endswith('.pdf'):
            logger.info('{} is skipped  ({}/{})'.format(fileName, index+1, len(conf.fileList)))
            continue
        else:
            logger.info('Processing File {}  ({}/{})'.format(fileName, index+1, len(conf.fileList)))

        filePath = conf.folder + fileName
        PagesImage  = pdf2image(filePath)
        PagesLayout = pdf2layout(filePath)

        if not PagesLayout == None:
            seg_rst = SemanticSegmentation(conf, PagesImage, PagesLayout)

            if conf.evaluate == True:
                Anno = annotation()
                pre, rec, f1 = estimate(seg_rst, Anno)
                EstimationWrite(pre, rec, f1, fileName, conf.eva_folder)

            if conf.save_image == True:
                ImageList = rst2image(conf, seg_rst, PagesImage, PagesLayout)
                ImageWrite(ImageList, fileName, conf.img_folder)

            if conf.save_text == True:
                jsonFile = rst2json(seg_rst)
                JsonWrite(jsonFile, fileName, conf.json_folder)

        c = str(input())
        if c == 'q':
            import sys
            sys.exit()

    logger.info("All file processed")