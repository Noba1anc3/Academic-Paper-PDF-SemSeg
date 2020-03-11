
def IOU(Box1, Box2):
    x1 = Box1[0]
    y1 = Box1[1]
    x2 = Box1[2]
    y2 = Box1[3]
    x3 = Box2[0]
    y3 = Box2[1]
    x4 = Box2[2]
    y4 = Box2[3]
    w1 = x2 - x1
    w2 = x4 - x3
    h1 = y2 - y1
    h2 = y4 - y3

    IOU_W = min(x1, x2, x3, x4) + w1 + w2 - max(x1, x2, x3, x4)
    IOU_H = min(y1, y2, y3, y4) + h1 + h2 - max(y1, y2, y3, y4)

    S1 = h1*w1
    S2 = h2*w2

    if IOU_W > 0 and IOU_H > 0:
        InterSection = IOU_H*IOU_W
        Union = S1 + S2 - InterSection
        return InterSection/Union
    else:
        return 0