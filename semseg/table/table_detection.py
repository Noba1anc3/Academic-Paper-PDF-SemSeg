from pdfminer.layout import *

from extraction.table.table_utils import *

minimum_row_number = 1        # 表格中应最少包含的行数
minimum_column_number = 1     # 表格中应最少包含的列数
horizontal_line_thres = 1     # 若两个水平线条的纵坐标之差小于horizontal_line_thres，则认为它们处于统一像素行
alignment_thres = 1           # 表格的水平边界线的两个端点横坐标差值小于alignment_thres
# 表格中不允许出现的词，用于减少识别false positive
special_words=('table', 'figure')
# 算法块的标志性开头，因为算法被识别成表格的几率很高，所以单独处理
algorithm_signal = ('algorithm', 'Algorithm')


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

def get_grouping_number(nums):
    '''
    将一堆数字进行分组，距离小于thres4的为一组
    :param nums: 一个列表，列表中存放多个数字
    :return: 返回分成了多少组
    '''
    groups = []
    for num in nums:
        find_group = False
        for group in groups:
            if abs(num - group) < horizontal_line_thres:
                find_group = True
                break
        if not find_group:
            groups.append(num)
    return len(groups)


def detetct_singal_column(sorted_curves, special_lines, text_lines, algorithm_lines):
    '''
    检测出单栏中的所有表格
    :param sorted_curves: 按照ｙ降序排列的本栏中的所有横线
    :param special_lines: 含有特殊单词的文本行
    :param text_lines: 所有文本行
    :return: 单栏中的所有表格，格式为[[左上x, 左上y, 右下x, 右下y], ...]
    '''
    # 将线条进行对齐分组，同时每一组内部不能含有special_words
    groups = []
    start = 0
    while start < len(sorted_curves):
        for end in range(len(sorted_curves) - 1, start - 1, -1):
            if abs(sorted_curves[start].x0 - sorted_curves[end].x0) < alignment_thres and \
                    abs(sorted_curves[start].x1 - sorted_curves[end].x1) < alignment_thres:

                # # 如果这两条线组成的矩形区域和特殊行有交集，那么就continue，否则，将这个区域加入备选组
                # contain_special_lines = False
                # for note in special_lines:
                #     rectangle_region = [sorted_curves[start].x0, sorted_curves[start].y1,
                #                         sorted_curves[end].x1, sorted_curves[end].y0]
                #     note_region = [note.x0, note.y1, note.x1, note.y0]
                #     if relation_between_regions(rectangle_region, note_region, 'INTERSECT'):
                #         contain_special_lines = True
                #         break
                # if contain_special_lines:
                #     continue

                group = sorted_curves[start:end + 1]
                groups.append(group)
                start = end + 1
                break

    # 线条数量少于1的不可能是表格
    groups_with_curves = []
    for group in groups:
        if len(group) > 1:
            groups_with_curves.append(group)

    # 去除算法块
    groups_without_algorithm = []
    for group in groups_with_curves:
        group_region = [group[0].x0, group[0].y1,
                        group[-1].x1, group[-1].y0]
        contain_algorithm = False
        for line in algorithm_lines:
            line_region = [line.x0, line.y1, line.x1, line.y0]
            if relation_between_regions(group_region, line_region, 'CONTAIN'):
                contain_algorithm = True
        if not contain_algorithm:
            groups_without_algorithm.append(group)


    # 表格内必须有多行多列textlines
    selected_groups = []
    for group in groups_without_algorithm:
        # 找出这个表格内的所有textline
        text_regions = []
        for text in text_lines:
            rectangle_region = [group[0].x0, group[0].y0, group[-1].x1, group[-1].y1]
            text_region = [text.x0, text.y1, text.x1, text.y0]
            if relation_between_regions(rectangle_region, text_region, 'CONTAIN'):
                text_regions.append(text)
        if len(text_regions) == 0:
            continue

        # textlines的行数和列数应该大于一定阈值
        # x分为左、中、右的原因是考虑到对齐方式可能是左对齐、居中、右对齐
        x_left = []
        x_mid = []
        x_right = []
        y = []
        for region in text_regions:
            x_left.append(region.x0)
            x_right.append(region.x1)
            x_mid.append((region.x0 + region.x1) / 2)
            y.append(region.y0)
        row_number = get_grouping_number(y)
        column_number_left = get_grouping_number(x_left)
        column_number_right = get_grouping_number(x_right)
        column_number_mid = get_grouping_number(x_mid)
        if row_number > minimum_row_number and column_number_left > minimum_column_number and \
                column_number_right > minimum_column_number and column_number_mid > minimum_column_number:
            selected_groups.append(group)

    # 生成左上+右下坐标形式
    tables = []
    for group in selected_groups:
        tables.append([group[0].x0, group[0].y0, group[-1].x1, group[-1].y1])
    return tables


def detect_table(page_layout):
    '''
    检测给定页面的所有表格
    :param page_layout: 由于pdfminer解析得到的布局信息
    :param special_words: 一些不可能出现在表格中的特殊词汇，用于减少false positive的数量
    :return: 当前页面的所有表格区域，格式为[[左上x, 左上y, 右下x, 右下y], ...]
    '''
    # 从布局信息中提取可能需要用的box，水平横线、文字行、以为特殊字段开头的行
    horizontal_curves = []
    text_lines = []
    special_lines = []
    algorithm_lines = []
    for box in page_layout:
        if isinstance(box, LTCurve) and abs(box.y1 - box.y0) < horizontal_line_thres:
            horizontal_curves.append(box)
        if isinstance(box, LTTextBoxHorizontal):
            for line in box:
                text_lines.append(line)
                if line.get_text().lower().startswith(special_words):
                    special_lines.append(line)
                if line.get_text().startswith(algorithm_signal):
                    algorithm_lines.append(line)

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
    left_tables = detetct_singal_column(left_curves, special_lines, text_lines, algorithm_lines)
    right_tables = detetct_singal_column(right_curves, special_lines, text_lines, algorithm_lines)
    tables = left_tables + right_tables

    return tables
