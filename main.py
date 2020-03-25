from utils.readWrite.read import *
from utils.readWrite.write import *

from semseg.semseg import *

from estimate.estClass import *
from estimate.jsonRead import jsonRead
from estimate.estimation import estimate

from utils.formatChange.pdf2xml import pdf2layout
from utils.formatChange.pdf2image import pdf2image
from utils.formatChange.result2json import rst2json
from utils.formatChange.result2image import rst2image

if __name__ == '__main__':
    logging = Logger(__name__)
    Logger.get_log(logging).info('System Start\n')

    Conf = Configuration()

    if Conf.evaluate:
        Est = Estimation()

    for index in range(len(Conf.fileList)):
        fileName = Conf.fileList[index]
        if not fileName.endswith('.pdf'):
            Logger.get_log(logging).info\
                ('{} is skipped  ({}/{})'.format
                 (fileName, index + 1, len(Conf.fileList)))
            continue
        else:
            Logger.get_log(logging).info(
                'Processing File - {}  ({}/{})'.format
                (fileName, index + 1, len(Conf.fileList)))

        filePath = Conf.folder + fileName
        PagesImage  = pdf2image(filePath)
        PagesLayout = pdf2layout(filePath)

        if not PagesLayout == None:
            semseg = SemanticSegmentation(Conf, PagesImage, PagesLayout)
            jsonFile = rst2json(Conf, fileName, semseg, PagesLayout)

            if Conf.evaluate:
                #jsonFile = jsonRead(fileName)
                Anno = annotation(fileName, len(PagesImage))
                if not Anno.Anno == []:
                    prfList = estimate(PagesImage, jsonFile, Anno, Conf.eva_img_folder)
                    Est.num_add(prfList)
                    EstimationWrite(prfList, fileName, Conf.eva_doc_folder)

            if Conf.save_image:
                ImageList = rst2image(Conf, semseg, PagesImage, PagesLayout)
                ImageWrite(ImageList, fileName, Conf.img_folder)

            if Conf.save_text:
                JsonWrite(jsonFile, fileName, Conf.json_folder)

            Logger.get_log(logging).info("File - {} Processed\n".format(fileName))

    if Conf.evaluate:
        prfList = Est.cal_total_score()
        EstimationWrite(prfList, 'Average.pdf', Conf.eva_folder)

    Logger.get_log(logging).info("All file processed")
