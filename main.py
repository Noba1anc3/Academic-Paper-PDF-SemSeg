
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

    total_p_num = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                   'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    total_r_num = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                   'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    total_f_num = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                   'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    total_p_area = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                    'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    total_r_area = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                    'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    total_f_area = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                    'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}
    valid_num = {'Title': 0, 'Author': 0, 'Text': 0, 'FigureNote': 0,
                 'TableNote': 0, 'Note': 0, 'PageNo': 0, 'Figure': 0, 'Table': 0, 'Cell': 0}

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
            jsonFile = rst2json(conf, fileName, semseg, PagesImage, PagesLayout)

            if conf.evaluate == True:
                Anno = annotation(fileName, len(PagesImage))
                #jsonFile = jsonRead(fileName)
                p_num, r_num, f_num, p_area, r_area, f_area = estimate(jsonFile, Anno)
                EstimationWrite(p_num, r_num, f_num, p_area, r_area, f_area, fileName, conf.eva_folder)

            for key in p_num.keys():
                if p_num[key] != 'NaN':
                    valid_num[key] += 1
                    total_p_num[key] += p_num[key]
                    total_r_num[key] += r_num[key]
                    total_f_num[key] += f_num[key]
                    total_p_area[key] += p_area[key]
                    total_r_area[key] += r_area[key]
                    total_f_area[key] += f_area[key]

            if conf.save_image == True:
                ImageList = rst2image(conf, semseg, PagesImage, PagesLayout)
                ImageWrite(ImageList, fileName, conf.img_folder)

            if conf.save_text == True:
                JsonWrite(jsonFile, fileName, conf.json_folder)

            Logger.get_log(logging).info("File - {} Processed\n".format(fileName))

    for key in total_p_num.keys():
        if valid_num[key] == 0:
            total_p_num[key] = 'NaN'
            total_r_num[key] = 'NaN'
            total_f_num[key] = 'NaN'
            total_p_area[key] = 'NaN'
            total_r_area[key] = 'NaN'
            total_f_area[key] = 'NaN'
        else:
            total_p_num[key] /= valid_num[key]
            total_r_num[key] /= valid_num[key]
            total_f_num[key] /= valid_num[key]
            total_p_area[key] /= valid_num[key]
            total_r_area[key] /= valid_num[key]
            total_f_area[key] /= valid_num[key]

    EstimationWrite(total_p_num, total_r_num, total_f_num,
                    total_p_area, total_r_area, total_f_area,
                    'AAAAA.pdf', conf.eva_folder)

    Logger.get_log(logging).info("All file processed")




