from pdfminer.layout import *

contain_thres = 0.7  # 区域1中包含区域2的面积大于contain_thres，则认为区域2在区域1内部
curve_thres = 0.4      # 考虑到表格线条可能倾斜，所以只要线条两端点的ｙ坐标相差不超过curve_thres，则认为是水平线条，竖直线条同理


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


def get_horizontal_curves(page_layout):
    """
    获取当前页面中的所有水平线条
    :param page_layout: 当前页面的布局信息
    :return: 水平线条对象列表
    """
    horizontal_curves = []
    for box in page_layout:
        if isinstance(box, LTCurve) and abs(box.y0 - box.y1) < curve_thres:
            horizontal_curves.append(box)
    return horizontal_curves


def get_vertical_curves(page_layout):
    """
    获取当前页面中的所有竖直线条
    :param page_layout: 当前页面的布局信息
    :return: 竖直线条对象列表
    """
    vertical_curves = []
    for box in page_layout:
        if isinstance(box, LTCurve) and abs(box.x0 - box.x1) < curve_thres:
            vertical_curves.append(box)
    return vertical_curves


def get_text_lines(page_layout):
    """
    获取当前页面中的所有文字行
    :param page_layout: 当前页面布局信息
    :return: 文字行的对象列表
    """
    text_lines = []
    for box in page_layout:
        if isinstance(box, LTTextBoxHorizontal):
            for line in box:
                text_lines.append(line)
    return text_lines

