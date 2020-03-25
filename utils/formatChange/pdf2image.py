from utils.logging.syslog import Logger
from pdf2image import convert_from_path
import numpy as np
import tempfile
import cv2

def pdf2image(fileName):

    with tempfile.TemporaryDirectory() as path:
        PagesImage = convert_from_path(fileName, output_folder = path)

    for index in range(len(PagesImage)):
        PageImage = PagesImage[index]
        PagesImage[index] = cv2.cvtColor(np.asarray(PageImage), cv2.COLOR_RGB2BGR)

    logging = Logger(__name__)
    Logger.get_log(logging).info('pdf2image Completed')
    logging.logger.handlers.clear()

    return PagesImage