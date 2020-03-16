
def BoxInterCheck(Box1, Box2):
    if IOU(Box1, Box2) > 0:
        if Box1[0] <= Box2[0] and Box1[2] >= Box2[2] and Box1[1] <= Box2[1] and Box1[3] >= Box2[3]:
            return False
        if Box2[0] <= Box1[0] and Box2[2] >= Box1[2] and Box2[1] <= Box1[1] and Box2[3] >= Box1[3]:
            return False
        return True
    return False

def BoxInsideCheck(Box1, Box2):
    # 检查Box2是否在Box1当中
    if Box1[0] <= Box2[0] and Box1[2] >= Box2[2] and Box1[1] <= Box2[1] and Box1[3] >= Box2[3]:
        return True
    else:
        return False

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
