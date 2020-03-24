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
    total_pre_num = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0,
                     'PageNo': 0.0, 'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}
    total_rec_num = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0,
                     'PageNo': 0.0, 'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}
    total_f1_num = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0,
                    'PageNo': 0.0, 'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}
    total_pre_area = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0,
                      'PageNo': 0.0, 'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}
    total_rec_area = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0,
                      'PageNo': 0.0, 'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}
    total_f1_area = {'Title': 0.0, 'Author': 0.0, 'Text': 0.0, 'FigureNote': 0.0, 'TableNote': 0.0, 'Note': 0.0,
                     'PageNo': 0.0, 'Figure': 0.0, 'Table': 0.0, 'Cell': 0.0}
    validnum = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0, 'TableNote': 0, 'Note': 0, 'PageNo': 0,
                'Figure': 0, 'Table': 0, 'Cell': 0}

    for index in range(len(conf.fileList)):
        fileName = conf.fileList[index]
        if not fileName.endswith('.pdf'):
            Logger.get_log(logging).info('{} is skipped  ({}/{})'.format(fileName, index + 1, len(conf.fileList)))
            continue
        else:
            Logger.get_log(logging).info(
                'Processing File - {}  ({}/{})'.format(fileName, index + 1, len(conf.fileList)))

        filePath = conf.folder + fileName
        PagesImage  = pdf2image(filePath)
        PagesLayout = pdf2layout(filePath)

        if not PagesLayout == None:
            semseg = SemanticSegmentation(conf, PagesImage, PagesLayout)
            jsonFile = rst2json(conf, fileName, semseg, PagesImage, PagesLayout)

            if conf.evaluate == True:
                #jsonFile = jsonRead(fileName)
                Anno = annotation(fileName, len(PagesImage))

                pre_num, rec_num, f1_num, pre_area, rec_area, f1_area = \
                    estimate(PagesImage, jsonFile, Anno, conf.eva_img_folder)
                EstimationWrite(pre_num, rec_num, f1_num,
                                pre_area, rec_area, f1_area,
                                fileName, conf.eva_doc_folder)

                for key in pre_num.keys():
                    if pre_num[key] != 'NaN':
                        validnum[key] += 1
                        total_pre_num[key] += pre_num[key]
                        total_rec_num[key] += rec_num[key]
                        total_f1_num[key] += f1_num[key]
                        total_pre_area[key] += pre_area[key]
                        total_rec_area[key] += rec_area[key]
                        total_f1_area[key] += f1_area[key]

            if conf.save_image == True:
                ImageList = rst2image(conf, semseg, PagesImage, PagesLayout)
                ImageWrite(ImageList, fileName, conf.img_folder)

            if conf.save_text == True:
                JsonWrite(jsonFile, fileName, conf.json_folder)

            Logger.get_log(logging).info("File - {} Processed\n".format(fileName))

    for key in total_pre_num.keys():
        if validnum[key] == 0:
            total_pre_num[key] = 'NaN'
            total_rec_num[key] = 'NaN'
            total_f1_num[key] = 'NaN'
            total_pre_area[key] = 'NaN'
            total_rec_area[key] = 'NaN'
            total_f1_area[key] = 'NaN'
        else:
            total_pre_num[key] /= validnum[key]
            total_rec_num[key] /= validnum[key]
            total_f1_num[key] /= validnum[key]
            total_pre_area[key] /= validnum[key]
            total_rec_area[key] /= validnum[key]
            total_f1_area[key] /= validnum[key]
            total_pre_num[key] = float(format(total_pre_num[key], '.2f'))
            total_rec_num[key] = float(format(total_rec_num[key], '.2f'))
            total_f1_num[key] = float(format(total_f1_num[key], '.2f'))
            total_pre_area[key] = float(format(total_pre_area[key], '.2f'))
            total_rec_area[key] = float(format(total_rec_area[key], '.2f'))
            total_f1_area[key] = float(format(total_f1_area[key], '.2f'))

    EstimationWrite(total_pre_num, total_rec_num, total_f1_num, total_pre_area,
                    total_rec_area, total_f1_area, 'Average.pdf', conf.eva_folder)

    Logger.get_log(logging).info("All file processed")
