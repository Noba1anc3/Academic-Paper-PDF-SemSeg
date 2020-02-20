
def overlap(lineA, lineB):
    lengthA = lineA[1] - lineA[0]
    lengthB = lineB[1] - lineB[0]

    if lineA[1] <= lineB[0]:
        return 0
    if lineA[0] >= lineB[1]:
        return 0
    if lineA[0] <= lineB[0] and lineB[1] <= lineA[1]:
        return 1
    if lineB[0] <= lineA[0] and lineA[1] <= lineB[1]:
        return 1

    lap = lineA[1] - lineB[0]
    if lap < min(lengthA, lengthB):
        return lap/min(lengthA, lengthB)
    else:
        lap = lineB[1] - lineA[0]
        return lap/min(lengthA, lengthB)

def get_liRatio(PageImage, PageLayout):
    #计算pdfminer分析出来的layout和pdf2image生成的image之间的尺寸比
    IMG_H = PageImage.shape[0]
    IMG_W = PageImage.shape[1]
    LAYOUT_H = PageLayout.y1
    LAYOUT_W = PageLayout.x1
    liRatioH = LAYOUT_H / IMG_H
    liRatioW = LAYOUT_W / IMG_W

    return [liRatioW, liRatioH]
