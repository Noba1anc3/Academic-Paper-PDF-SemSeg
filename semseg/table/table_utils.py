from pdfminer.layout import *
from semseg.table.table import *

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


def get_words(line):
    """
    给定一个文本行，将其拆分成多个单词
    :param line: 待拆分的文本行
    :return: 多个单词组成的列表
    """
    words = []
    word = LTTextWordsHorizontal()
    last_char = ''
    for item in line:
        last_char = item.get_text()
        if isinstance(item, LTChar):
            word.add(item)
        else:
            words.append(word)
            word = LTTextWordsHorizontal()
    if last_char != ' ' and last_char != '\n' and last_char != '':
        words.append(word)

    return words


def split_line_by_separators(line, separators):
    """
    使用区间对文字行进行分割，所有区间与文字行中的空格位置均有重合才可分割，separators为空列表的情况也可以处理
    :param line: 待分割的文字行
    :param separators: 分割区间或分割符，按照separators递增排序
    :return: 分割后的文字行列表
    """
    # 如果separators是分割符，将其转换为分割区间
    intervals = []
    for sep in separators:
        if type(sep).__name__ == 'list':
            intervals.append(sep)
        else:
            intervals.append([sep, sep])

    # 获取该文字行的所有空格
    words = get_words(line)
    spaces = []
    if len(words) == 0:
        return []
    prev = words[0]
    for word in words:
        spaces.append([prev.x1, word.x0])
        prev = word
    spaces = spaces[1:]

    # 找到分割点
    split_points = []
    for inter in intervals:
        selected_index = -1
        maximum_intersect_length = 0
        for index in range(len(spaces)):
            space = spaces[index]
            intersect_length = min(space[1], inter[1]) - max(space[0], inter[0])
            if intersect_length >= maximum_intersect_length:
                selected_index = index
                maximum_intersect_length = intersect_length
        if selected_index == -1:     # 表示有一个分割符无法找到自己的位置，则认为整行不可分
            return [line]
        else:
            split_points.append(selected_index)
    split_points.append(len(words) - 1)

    # 根据上面找到的分割点，对文字行进行分割
    split_lines = []
    start = 0
    for point in split_points:
        s_line = LTTextWordsHorizontal()
        for index in range(start, point + 1):
            word = words[index]
            s_line.combine(word)
        if s_line.get_text() != '':
            split_lines.append(s_line)
        start = point + 1
    return split_lines
