
from utils.pdfminer import *
from utils.layout import *
from extraction import *

from logzero import logger
import numpy as np

if __name__ == '__main__':
    if not os.path.exists('example/analysis_result/'):
        os.mkdir('example/analysis_result/')
    fileList = sorted(os.listdir('example/pdf_file'))
    fileNum = len(fileList)

    for index in range(fileNum):
        fileName = fileList[index]

        if not fileName.endswith('.pdf'):
            logger.info('{} is skipped  ({}/{})'.format(fileName, index+1, fileNum))
            continue
        else:
            logger.info('Processing File {}  ({}/{})'.format(fileName, index+1, fileNum))

        filePath = 'example/pdf_file/' + fileName
        PagesLayout = layout_analysis(filePath)
        PagesImage  = pdf_to_image(filePath)

        for PageNo in range(len(PagesImage)):
            PageImage = PagesImage[PageNo]
            PageLayout = PagesLayout[PageNo]

            PageImage = cv2.cvtColor(np.asarray(PageImage), cv2.COLOR_RGB2BGR)
            LayoutHeight = PageLayout.height
            liRatio = get_liRatio(PageImage, PageLayout)

            if PageNo == 0:
                Title, titleIndex, titleError = titleExtraction(PageLayout)
                if titleError:
                    logger.info('Unexpected Error when Locating Title in Page {} of File {}'.format(PageNo, fileName))
                else:
                    BBoxes = getBoundingBoxes(LayoutHeight, Title, liRatio)
                    PageImage = drawBox(PageImage, LTTitle, BBoxes)

                Author = AuthorExtraction(PageLayout, titleIndex)
                BBoxes = getBoundingBoxes(LayoutHeight, Author, liRatio)
                PageImage = drawBox(PageImage, LTAuthor, BBoxes)
                cv2.imshow('1', PageImage)

                Anno_Image = layoutImage(PageImage, PageLayout, liRatio)
                cv2.imshow('2', Anno_Image)
                cv2.waitKey(0)

                continue
            # if not os.path.exists('example/analysis_result/' + fileName[:-4]):
            #     os.mkdir('example/analysis_result/' +fileName[:-4])
            # cv2.imwrite('example/analysis_result/' + fileName[:-4] + '/' + str(PageNo) + '.jpg', Anno_Image)

    logger.info("All file processed")