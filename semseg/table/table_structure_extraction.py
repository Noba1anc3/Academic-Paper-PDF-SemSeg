import re
from semseg.table.table_utils import *
from semseg.table.column_partition import column_partition
from semseg.table.row_partition import row_partition


def split_line_into_words(line):
    """
    将文字行直接按照单词划分
    :param line: 待划分的文字航
    :return: 分割形成的列表
    """
    words = get_words(line)
    words_list = []
    for word in words:
        words_list.append(word)
    return words_list


def get_digit_separators(line):
    """
    对于有连续数字的行进行进一步分割，如'string 23 44'，则分割点为string之和23之后
    :param line: 待分割的文字行
    :return: 分割点列表
    """
    separators = []
    digit_list = []
    words = get_words(line)
    value = re.compile(r'^[-+]?([0-9]+|([0-9]+\.[0-9]+))$')  # 正则表达式，匹配整数、浮点数
    for word in words:
        if value.match(word.get_text()):
            digit_list.append(word)
        else:
            if len(digit_list) > 1:
                separators.append(digit_list[0].x0)
                for digit in digit_list:
                    separators.append(digit.x1)
            digit_list = []
    if len(digit_list) > 1:  # 针对连续数字在结尾的情况单独处理，如'sep 52 56'
        separators.append(digit_list[0].x0)
        for digit in digit_list:
            separators.append(digit.x1)

    # 分割符不需要包括开头和结尾坐标，只需要中间左边，如果存在，则删去
    if len(separators) > 0:
        if separators[0] == line.x0:
            separators = separators[1:]
        if separators[-1] == line.x1:
            separators = separators[:-1]

    return separators


def get_percent_separators(line):
    """
    对于有百分号的文字行进行分割
    :param line: 待分割的文字行
    :return: 分隔符列表
    """
    # 由于数字和百分号可能分离，先将分离的百分数合并起来
    words = get_words(line)
    merged_words = []
    for word in words:
        if word.get_text() == '%':
            if len(merged_words) > 0:
                merged_words[-1].combine(word)
        else:
            merged_words.append(word)

    separators = []
    percent_list = []
    for word in merged_words:
        if word.get_text().endswith('%'):
            percent_list.append(word)
        else:
            if len(percent_list) > 1:
                separators.append(percent_list[0].x0)
                for percent in percent_list:
                    separators.append(percent.x1)
            percent_list = []
    if len(percent_list) > 0:
        separators.append(percent_list[0].x0)
        for percent in percent_list:
            separators.append(percent.x1)

    # 分割符不需要包括开头和结尾坐标，只需要中间左边，如果存在，则删去
    if len(separators) > 0:
        if separators[0] == line.x0:
            separators = separators[1:]
        if separators[-1] == line.x1:
            separators = separators[:-1]

    return separators


def get_children(children):
    """
    将children转换成需要的形式返回
    :param children:
    :return:
    """
    if len(children) == 0:
        return children
    else:
        res = []
        for child in children:
            res.append([[child.x0, child.y1, child.x1, child.y0], child.start_row, child.end_row, child.start_col,
                        child.end_col, child.get_text(), get_children(child.children)])
        return res


def extraction(page_layout, table_region):
    """
    对整个表格做解析
    :param page_layout: 当前页面布局信息
    :param table_region: 要解析的表格区域
    :return:
    """
    # ===============================================
    # 通用列切分规则
    # 取出表格范围内的所有文字行
    initial_cells = []
    text_lines = get_text_lines(page_layout)
    for line in text_lines:
        line_region = [line.x0, line.y1, line.x1, line.y0]
        if relation_between_regions(table_region, line_region, 'CONTAIN'):
            initial_cells.append(line)

    # 通过表格中的竖直线条进一步分割文字行
    v_curve_split_cells = []
    vertical_curves = get_vertical_curves(page_layout)
    for cell in initial_cells:
        horizontal_separators = []
        for curve in vertical_curves:
            if cell.x0 < curve.x0 < cell.x1 and \
                    min(cell.y1, curve.y1) - max(cell.y0, curve.y0) > 0.5 * (cell.y1 - cell.y0):
                horizontal_separators.append(curve.x0)
        split_lines = split_line_by_separators(cell, horizontal_separators)
        v_curve_split_cells += split_lines

    # 对存在连续多个数字的行进行分割
    digit_split_cells = []
    for cell in v_curve_split_cells:
        digit_separators = get_digit_separators(cell)
        digit_split_cells += split_line_by_separators(cell, digit_separators)

    # 根据百分号进行分割
    percent_split_cells = []
    for cell in digit_split_cells:
        percent_separators = get_percent_separators(cell)
        percent_split_cells += split_line_by_separators(cell, percent_separators)

    # ===========================================================
    # 针对数据集的规则
    # 对列做切分
    horizontal_curves = get_horizontal_curves(page_layout)
    rows, span_row_cells, remain_cells, column_intervals = column_partition(table_region, percent_split_cells,
                                                                            horizontal_curves)
    column_header_end_row = -1
    if len(column_intervals) <= 2:    # 只有两列的表格必定没有列表头
        for row in rows:
            for cell in row:
                cell.children = []
                cell.father = []
                remain_cells.append(cell)
                column_header_end_row = max(column_header_end_row, cell.end_row)
        for cell in span_row_cells:
            remain_cells.append(cell)
            column_header_end_row = max(column_header_end_row, cell.end_row)
        rows = []
        span_row_cells = []

    # =============================================================
    # 进行行切割
    row_header_cells, body_cells, row_intervals = row_partition(remain_cells, horizontal_curves, column_intervals,
                                                                table_region, column_header_end_row)

    # 转换成需要的形式返回
    column_header = []
    for row in rows:
        for cell in row:
            if cell.father is None:
                column_header.append([[cell.x0, cell.y1, cell.x1, cell.y0], cell.start_row, cell.end_row,
                                      cell.start_col, cell.end_col, cell.get_text(), cell.children])
    for cell in column_header:
        cell[6] = get_children(cell[6])
    for cell in span_row_cells:
        column_header.append([[cell.x0, cell.y1, cell.x1, cell.y0], cell.start_row, cell.end_row, cell.start_col,
                           cell.end_col, cell.get_text(), cell.children])
    
    row_header = []
    for cell in row_header_cells:
        row_header.append([[cell.x0, cell.y1, cell.x1, cell.y0], cell.start_row, cell.end_row, cell.start_col,
                           cell.end_col, cell.get_text(), cell.children])
    
    body = []
    for cell in body_cells:
        body.append([[cell.x0, cell.y1, cell.x1, cell.y0], cell.start_row, cell.end_row, cell.start_col, cell.end_col,
                     cell.get_text()])

    return column_header, row_header, body
