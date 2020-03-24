from semseg.table.table import *


def get_row_intervals(priori_cells, assistant_cells):
    """
    将由单元格得到行区间
    :param cells: 单元格
    :return: 区间列表
    """
    # 暂定：以第一列为优先，后续列为协助划分行
    assistant_cells = sorted(assistant_cells, key=lambda ce: ce.y1 - ce.y0)
    cells = priori_cells + assistant_cells
    row_intervals = []
    for cell in cells:
        intersect_number = 0
        intersect_index = -1
        for index in range(len(row_intervals)):
            interval = row_intervals[index]
            if min(interval[0], cell.y1) > max(interval[1], cell.y0):
                intersect_number += 1
                intersect_index = index
        if intersect_number == 0:
            row_intervals.append([cell.y1, cell.y0])
        elif intersect_number == 1:
            row_intervals[intersect_index][0] = max(row_intervals[intersect_index][0], cell.y1)
            row_intervals[intersect_index][1] = min(row_intervals[intersect_index][1], cell.y0)

    return row_intervals


def merge_cells_by_horizontal_curves(cells, horizontal_curves):
    """
    两个水平线条之间的单元格全部合并
    :param cells: 表格中单列的单元格
    :param horizontal_curves: 贯穿表格的水平线条
    :return: 合并后的所有单元格，是否进行了合并操作
    """
    merge_lists = []
    flag = []
    for cell in cells:
        flag.append(1)
    horizontal_curves = sorted(horizontal_curves, key=lambda cur: cur.y0, reverse=True)
    for curve in horizontal_curves:
        merge_lists.append([])
        for index in range(len(cells)):
            cell = cells[index]
            if flag[index] == 1:
                if (cell.y0 + cell.y1) / 2 > curve.y0:
                    merge_lists[-1].append(cell)
                    flag[index] = 0
        if len(merge_lists[-1]) == 0:
            merge_lists = merge_lists[:-1]
    merge_lists.append([])
    for index in range(len(cells)):
        cell = cells[index]
        if flag[index] == 1:
            merge_lists[-1].append(cell)
    if len(merge_lists[-1]) == 0:
        merge_lists = merge_lists[:-1]

    merged = False
    merged_cells = []
    for m_list in merge_lists:
        if len(m_list) > 1:
            merged = True
        m_list = sorted(m_list, key=lambda ce: ce.y0, reverse=True)
        temp_cell = LTTextWordsHorizontal()
        for cell in m_list:
            temp_cell.combine(cell)
        merged_cells.append(temp_cell)

    return merged_cells, merged


def divide_cells_by_column_intervals(cells, column_intervals):
    """
    将单元格分配给不同的列区间
    :param cells: 待分配的单元格
    :param column_intervals: 列区间
    :return: 分好组的单元格，以及跨列单元格
    """
    cell_groups = []
    span_column_cells = []
    for interval in column_intervals:
        cell_groups.append([])
    for cell in cells:
        find = False
        for index in range(len(column_intervals)):
            interval = column_intervals[index]
            if min(cell.x1, interval[1]) - max(cell.x0, interval[0]) > 0.8 * (cell.x1 - cell.x0):
                cell_groups[index].append(cell)
                find = True
                break
        if not find:
            span_column_cells.append(cell)

    return cell_groups, span_column_cells


def shrink_cells_by_horizontal_curves(cells, horizontal_curves):
    """
    利用水平横线缩小单元格高度，使得框更加准确
    :param cells: 待缩小单元格
    :param horizontal_curves: 当前页面所有水平横线
    :return: 缩小后的所有单元格
    """
    for cell in cells:
        for curve in horizontal_curves:
            if cell.y0 < curve.y0 < cell.y1 and \
                    min(cell.x1, curve.x1) - max(cell.x0, curve.x0) > 0.5 * (cell.x1 - cell.x0):
                if curve.y0 > (cell.y0 + cell.y1) / 2:
                    cell.y1 = curve.y0 - 0.1
                else:
                    cell.y0 = curve.y0 + 0.1

    return cells


def further_shrink_cells(cells, column_intervals):
    """
    通过使同一列上下单元格不得有重合部分来进一步缩小单元格
    :param cells: 待缩小的单元格
    :param column_intervals: 列区间
    :return: 缩小后的单元格
    """
    groups, span_column_cells = divide_cells_by_column_intervals(cells, column_intervals)

    for group in groups:
        group = sorted(group, key=lambda ce: ce.y0 + ce.y1, reverse=True)
        for index in range(len(group) - 1):
            current_cell = group[index]
            below_cell = group[index + 1]
            if current_cell.y0 < below_cell.y1:
                below_cell.y1 = current_cell.y0

    res_cells = []
    for group in groups:
        for cell in group:
            res_cells.append(cell)
    for cell in span_column_cells:
        res_cells.append(cell)

    return res_cells


def distribute_row_number(cells, row_intervals, column_header_end_row):
    """
    分配行号
    :param cells: 待分配行号的单元格
    :param row_intervals: 行区间
    :param column_header_end_row: 列表头结束的行，分配行号应该从这个数字之后开始分配
    :return: 无返回值
    """
    row_intervals = sorted(row_intervals, key=lambda inter: inter[0], reverse=True)
    for cell in cells:
        for index in range(len(row_intervals)):
            interval = row_intervals[index]
            find = False
            if (min(cell.y1, interval[0]) - max(cell.y0, interval[1])) > 0.8 * (cell.y1 - cell.y0):
                cell.start_row = column_header_end_row + 1 + index
                cell.end_row = column_header_end_row + 1 + index
                find = True

        if not find:
            for index in range(len(row_intervals)):
                interval = row_intervals[index]
                if interval[1] <= cell.y1 <= interval[0]:
                    if min(interval[0], cell.y1) - max(interval[1], cell.y0) > 1:
                        cell.start_row = column_header_end_row + 1 + index
                    else:
                        cell.start_row = column_header_end_row + 1 + index + 1
                if interval[1] <= cell.y0 <= interval[0]:
                    if min(interval[0], cell.y1) - max(interval[1], cell.y0) > 1:
                        cell.end_row = column_header_end_row + 1 + index
                    else:
                        cell.end_row = column_header_end_row + 1 + index - 1


def row_partition(initial_cells, horizontal_curves, column_intervals, table_region, column_header_end_row):
    """

    :param initial_cells:
    :param horizontal_curves:
    :param column_intervals:
    :param table_region:
    :param column_header_end_row:
    :return:
    """
    # 找出贯穿整个表格的线条
    selected_curves = []
    for curve in horizontal_curves:
        if abs(curve.x0 - table_region[0]) < 1 and abs(curve.x1 - table_region[2]) < 1 and \
                table_region[3] < curve.y0 < table_region[1]:
            selected_curves.append(curve)

    # 列数为1的特殊情况，必定是横线分割单元格
    if len(column_intervals) == 1:
        body_cells, _ = merge_cells_by_horizontal_curves(initial_cells, selected_curves)
        body_cells = shrink_cells_by_horizontal_curves(body_cells, horizontal_curves)
        body_cells = further_shrink_cells(body_cells, column_intervals)
        row_intervals = get_row_intervals([], body_cells)
        distribute_row_number(body_cells, row_intervals, column_header_end_row)
        return [], body_cells, row_intervals

    # 列数为2的情况，若第一列中每一行只有单行，则为横线分割单元格，否则和其他表格情况一起处理
    cell_groups, span_column_cells = divide_cells_by_column_intervals(initial_cells, column_intervals)
    if len(column_intervals) == 2:
        row_header_cells, merged = merge_cells_by_horizontal_curves(cell_groups[0], selected_curves)
        if not merged:
            body_cells, _ = merge_cells_by_horizontal_curves(cell_groups[1], selected_curves)
            row_header_cells = shrink_cells_by_horizontal_curves(row_header_cells, horizontal_curves)
            row_header_cells = further_shrink_cells(row_header_cells, column_intervals)
            body_cells = shrink_cells_by_horizontal_curves(body_cells, horizontal_curves)
            body_cells = further_shrink_cells(body_cells, column_intervals)
            row_intervals = get_row_intervals(row_header_cells, body_cells)
            distribute_row_number(row_header_cells + body_cells, row_intervals, column_header_end_row)
            return row_header_cells, body_cells, []

    # 除去前面两种情况的正常情况
    # 默认第一列为行表头
    row_header_cells = []
    for cell in cell_groups[0]:
        row_header_cells.append(cell)

    body_cells = []
    groups = cell_groups[1:]
    for group in groups:
        for cell in group:
            body_cells.append(cell)
    for cell in span_column_cells:
        body_cells.append(cell)

    # 根据行表头划分行区间
    row_header_cells = shrink_cells_by_horizontal_curves(row_header_cells, horizontal_curves)
    row_header_cells = further_shrink_cells(row_header_cells, column_intervals)
    body_cells = shrink_cells_by_horizontal_curves(body_cells, horizontal_curves)
    body_cells = further_shrink_cells(body_cells, column_intervals)
    row_intervals = get_row_intervals(row_header_cells, body_cells)
    distribute_row_number(row_header_cells + body_cells, row_intervals, column_header_end_row)

    # 还未处理的情况：跨行的行表头，跨行的表体，多级表头的情况

    return row_header_cells, body_cells, row_intervals
