import cv2

def ImageWrite(ImageList, fileName, fileFolder):
    for index in range(len(ImageList)):
        Image = ImageList[index]
        imgName = fileName[:-4] + '_' + str(index) + '.jpg'
        cv2.imwrite(fileFolder + imgName, Image)

def JsonWrite(JsonFile, fileName, fileFolder):
    pass

def EstimationWrite(pre, rec, f1, fileName, fileFolder):
    pass