contain_thres = 0.8  # 区域1中包含区域2的面积大于contain_thres，则认为区域2在区域1内部


def relation_between_regions(region1, region2, relation):
    """
    region1和region两块矩形区域之间是否存在关系relation
    :param region1: 区域1的坐标，格式为[左上x, 左上y, 右下x, 右下y]
    :param region2: 区域2的坐标，格式为[左上x, 左上y, 右下x, 右下y]
    :param relation: 需要判断的关系，'CONTAIN'：区域1包含区域2，'INTERSECT'：两区域有交集
    :return: 两区域满足关系relation则返回True，否则返回False
    """
    width = min(region1[2], region2[2]) - max(region1[0], region2[0])
    height = min(region1[1], region2[1]) - max(region1[3], region2[3])
    res = False

    if relation == 'INTERSECT':
        res = width > 0 and height > 0
    elif relation == 'CONTAIN':
        intersection = width * height
        area = (region2[2] - region2[0]) * (region2[1] - region2[3])
        res = width > 0 and height > 0 and (intersection / area) > contain_thres

    return res
