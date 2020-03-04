from pdfminer.layout import *

from extraction.table.table_utils import *

minimum_cell_number = 4       # 一个表格中应该至少包含多少个单元格
horizontal_line_thres = 1     # 若两个水平线条的纵坐标之差小于horizontal_line_thres，则认为它们处于统一像素行
alignment_thres = 1           # 表格的水平边界线的两个端点横坐标差值小于alignment_thres
# 表格中不允许出现的词，用于减少识别false positive
special_words=('table', 'Table', 'TABLE')
# 算法块的标志性开头，因为算法被识别成表格的几率很高，所以单独处理
algorithm_signal = ('Algorithm', 'Figure')


def merge_sort(lines):
    """
    归并排序将水平线条按y降序排列
    :param lines: 所有线条的列表
    :return: 按y坐标从大到小排序的线条列表
    """
    n = len(lines)
    if n < 2:
        return lines

    mid = (n - 1) // 2
    left = merge_sort(lines[0:mid + 1])
    right = merge_sort(lines[mid + 1:n])

    # 归并排序的merge过程
    sorted_lines = []
    while len(left) > 0 and len(right) > 0:
        if left[0].y0 > right[0].y0:
            sorted_lines.append(left[0])
            left = left[1:len(left)]
        else:
            sorted_lines.append(right[0])
            right = right[1:len(right)]
    while len(left) > 0:
        sorted_lines.append(left[0])
        left = left[1:len(left)]
    while len(right) > 0:
        sorted_lines.append(right[0])
        right = right[1:len(right)]

    return sorted_lines


def divide_curves_into_groups(sorted_curves, special_lines):
    """
    将水平线条分成多组，每一组作为表格的初始候选者
    :param sorted_curves: 按y坐标降序排列的水平线条
    :param special_lines: 不能出现在表格中的特殊字符，不会将它们划入同一个组内
    :return: 根据一定规则初步分出的多个组
    """
    groups = []
    start = 0
    while start < len(sorted_curves):
        for end in range(len(sorted_curves) - 1, start - 1, -1):
            if abs(sorted_curves[start].x0 - sorted_curves[end].x0) < alignment_thres and \
                    abs(sorted_curves[start].x1 - sorted_curves[end].x1) < alignment_thres:

                # 如果这两条线组成的矩形区域和特殊行有交集，那么就continue，否则，将这个区域加入备选组
                contain_special_lines = False
                rectangle_region = [sorted_curves[start].x0, sorted_curves[start].y1,
                                    sorted_curves[end].x1, sorted_curves[end].y0]
                for line in special_lines:
                    note_region = [line.x0, line.y1, line.x1, line.y0]
                    if relation_between_regions(rectangle_region, note_region, 'INTERSECT'):
                        contain_special_lines = True
                        break

                if not contain_special_lines:
                    group = sorted_curves[start:end + 1]
                    groups.append(group)
                    start = end + 1
                    break
    return groups


def exclude_algorithms(groups, algorithm_lines):
    """
    删除可能的算法框
    :param groups: 原始的多个组
    :param algorithm_lines: 含有算法标志的行
    :return: 删除后剩余的多个组
    """
    remain_groups = []
    for group in groups:
        group_region = [group[0].x0, group[0].y1, group[-1].x1, group[-1].y0]
        contain = False
        for element in algorithm_lines:
            element_region = [element.x0, element.y1, element.x1, element.y0]
            if relation_between_regions(group_region, element_region, 'CONTAIN'):
                contain = True
                break
        if not contain:
            remain_groups.append(group)
    return remain_groups


def exclude_figures_and_rects(groups, figures_and_rects):
    """
    删除组中可能的图片和非表格矩形框
    :param groups: 原始的多个组
    :param figures_and_rects: 图片和矩形框对象列表
    :return: 删除后剩余的多个组
    """
    remain_groups = []
    for group in groups:
        group_region = [group[0].x0, group[0].y1, group[-1].x1, group[-1].y0]
        contain = False
        for element in figures_and_rects:
            element_region = [element.x0, element.y1, element.x1, element.y0]
            if relation_between_regions(element_region, group_region, 'CONTAIN'):
                contain = True
                break
        if not contain:
            remain_groups.append(group)
    return remain_groups


def get_cells_number(group, text_lines):
    """
    计算某个表格候选区域内的文字行的数量，用以大概估计单元格数量是否低于某个阈值
    :param group: 表格候选者
    :param text_lines: 当前页面所有文字行
    :return: 区域内文字的数量
    """
    count = 0
    group_region = [group[0].x0, group[0].y1, group[-1].x1, group[-1].y0]
    for line in text_lines:
        line_region = [line.x0, line.y1, line.x1, line.y0]
        if relation_between_regions(group_region, line_region, 'CONTAIN'):
            count += 1
    return count


def detetct_singal_column(sorted_curves, elements_dict):
    """
    检测出单栏中的所有表格
    :param sorted_curves: 按照ｙ降序排列的本栏中的所有横线
    :param elements_dict: 页面中其他元素成分组成的词典
    """

    # 将词典中的各成分提取出来
    text_lines = elements_dict['text_lines']
    figures = elements_dict['figures']
    rects = elements_dict['rects']
    special_lines = []
    algorithm_lines = []
    for line in text_lines:
        if line.get_text().lower().startswith(special_words):
            special_lines.append(line)
        if line.get_text().startswith(algorithm_signal):
            algorithm_lines.append(line)

    # 将排好序的线条初步分组，每一组为一个表格区域的候选者
    initial_groups = divide_curves_into_groups(sorted_curves, special_lines)

    # 水平线条数量小于等于1的不可能是表格（后续可能需要优化的地方）
    groups_with_curves = []
    for group in initial_groups:
        if len(group) > 1:
            groups_with_curves.append(group)

    # 去除算法块
    groups_without_algorithm_lines = exclude_algorithms(groups_with_curves, algorithm_lines)

    # 去除图片和非表的矩形框
    groups_without_figures_and_rects = exclude_figures_and_rects(groups_without_algorithm_lines, figures + rects)

    # 表格中单元格数量必须达到一定阈值
    selected_groups = []
    for group in groups_without_figures_and_rects:
        if get_cells_number(group, text_lines) >= minimum_cell_number:
            selected_groups.append(group)

    # 生成左上+右下坐标形式
    tables = []
    for group in selected_groups:
        tables.append([group[0].x0, group[0].y0, group[-1].x1, group[-1].y1])
    return tables


def detect_table(page_layout):
    """
    检测给定页面的所有表格
    :param page_layout: 由于pdfminer解析得到的布局信息
    :param special_words: 一些不可能出现在表格中的特殊词汇，用于减少false positive的数量
    :return: 当前页面的所有表格区域，格式为[[左上x, 左上y, 右下x, 右下y], ...]
    """
    # 从布局信息中提取可能需要用的box，水平横线、文字行、以为特殊字段开头的行
    horizontal_curves = get_horizontal_curves(page_layout)
    text_lines = get_text_lines(page_layout)
    figures = get_figures(page_layout)
    rects = get_rects(page_layout)

    # 将所有需要使用到的不同类别（除线条外）的页面元素放入字典中，使得参数列表更加清晰
    elements_dict = {
        'text_lines': text_lines,
        'figures': figures,
        'rects': rects
    }

    # 将所有线条按照y坐标降序排列，便于后续操作
    sorted_curves = merge_sort(horizontal_curves)

    # 版面可能是单栏或者两栏
    # 表格可能分布整个版面的正中间，也可能分布在两栏中的任意一栏，下面的代码可以统一处理这两种情况
    left_curves, right_curves = [], []
    for line in sorted_curves:
        if line.x0 + line.x1 < page_layout.x1 - page_layout.x0:
            left_curves.append(line)
        else:
            right_curves.append(line)

    left_tables = detetct_singal_column(left_curves, elements_dict)
    right_tables = detetct_singal_column(right_curves, elements_dict)

    return left_tables + right_tables
