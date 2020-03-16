
from utils.readWrite.read import *
from utils.readWrite.write import *

from semseg.semseg import *
from estimate.estimation import estimate
from estimate.jsonRead import jsonRead

from utils.formatChange.pdf2xml import pdf2layout
from utils.formatChange.pdf2image import pdf2image
from utils.formatChange.result2json import rst2json
from utils.formatChange.result2image import rst2image

import sys
sys.dont_write_bytecode = True

if __name__ == '__main__':
    logging = Logger(__name__)
    Logger.get_log(logging).info('System Start\n')

    conf = Configuration()

    for index in range(len(conf.fileList)):
        fileName = conf.fileList[index]
        if not fileName.endswith('.pdf'):
            Logger.get_log(logging).info('{} is skipped  ({}/{})'.format(fileName, index+1, len(conf.fileList)))
            continue
        else:
            Logger.get_log(logging).info('Processing File - {}  ({}/{})'.format(fileName, index+1, len(conf.fileList)))

        filePath = conf.folder + fileName
        PagesImage  = pdf2image(filePath)
        PagesLayout = pdf2layout(filePath)

        if not PagesLayout == None:
            semseg = SemanticSegmentation(conf, PagesImage, PagesLayout)

        if conf.evaluate == True:
            Anno = annotation(fileName, len(PagesLayout))
            pre, rec, f1 = estimate(semseg, Anno)
            EstimationWrite(pre, rec, f1, fileName, conf.eva_folder)

            if conf.save_image == True:
                ImageList = rst2image(conf, semseg, PagesImage, PagesLayout)
                ImageWrite(ImageList, fileName, conf.img_folder)

            if conf.save_text == True:
                jsonFile = rst2json(conf, fileName, semseg, PagesImage, PagesLayout)
                JsonWrite(jsonFile, fileName, conf.json_folder)

            Logger.get_log(logging).info("File - {} Processed\n".format(fileName))

        # c = str(input())
        # if c == 'q':
        #     import sys
        #     sys.exit()

    Logger.get_log(logging).info("All file processed")




