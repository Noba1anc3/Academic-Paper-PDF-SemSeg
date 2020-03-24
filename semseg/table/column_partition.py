from semseg.table.table_utils import *
from semseg.table.table import *

alignment_thres = 1  # 表格的水平边界线的两个端点横坐标差值小于alignment_thres


def divide_table_cells_by_horizontal_separator(all_cells, separator):
    """
    根据给定的水平线条，将所有单元格分成上下两部分
    :param all_cells: 待分单元格
    :param separator: 水平分割线
    :return: above_cells, below_cells分别为水平线的上方、下方的单元格
    """
    above_cells = []
    below_cells = []
    for cell in all_cells:
        if (cell.y0 + cell.y1) / 2 > separator.y0:
            above_cells.append(cell)
        else:
            below_cells.append(cell)
    return above_cells, below_cells


def separate_row_header_from_body(table_region, table_cells, horizontal_curves):
    """
    将表格部分初步分为行表头和表体，这个分离中存在False Positive的情况
    :return:
    """
    # 找出那些在表格范围内且贯穿整个表格的水平线条
    # horizontal_curves = get_horizontal_curves(page_layout)
    horizontal_separators = []
    for curve in horizontal_curves:
        if table_region[3] < curve.y0 < table_region[1] and \
                abs(table_region[0] - curve.x0) < alignment_thres and \
                abs(table_region[2] - curve.x1) < alignment_thres:
            horizontal_separators.append(curve)

    # 将行表头和非行表头单元格进行初步分离，这个分离的不准确之处仅在于有些表格没有行表头
    row_header_cells = None
    body_cells = None
    if len(horizontal_separators) == 0:
        # 不存在表头
        row_header_cells = []
        body_cells = table_cells
    elif len(horizontal_separators) > 0:  # 这是存在行表头的必要条件
        # 将线条按照y坐标降序排列
        sorted_separators = sorted(horizontal_separators, key=lambda cur: cur.y0, reverse=True)

        # 找出行表头的所有单元格
        for separator in sorted_separators:
            row_header_cells, body_cells = divide_table_cells_by_horizontal_separator(table_cells, separator)
            if len(row_header_cells) > 0:
                break

    if len(body_cells) == 0:
        body_cells = row_header_cells
        row_header_cells = []

    return row_header_cells, body_cells


def get_column_intervals(intervals, prior_cells, assistant_cells):
    """
    利用cells辅助划分列
    :param intervals: 原始已有的列区间
    :param prior_cells: 优先用于划分的单元格
    :param assistant_cells: 辅助划分的单元格
    :return: 划分后的intervals
    """
    initial_null = False
    if len(intervals) == 0:
        initial_null = True

    sorted_assistant_cells = sorted(assistant_cells, key=lambda ce: ce.x1 - ce.x0, reverse=False)
    cells = prior_cells + sorted_assistant_cells
    for cell in cells:
        intersect_number = 0
        intersect_index = -1
        for index in range(len(intervals)):
            interval = intervals[index]
            if min(interval[1], cell.x1) > max(interval[0], cell.x0):
                intersect_number += 1
                intersect_index = index
        if intersect_number == 0 and initial_null:
            intervals.append([cell.x0, cell.x1])
        elif intersect_number == 1:
            intervals[intersect_index][0] = min(intervals[intersect_index][0], cell.x0)
            intervals[intersect_index][1] = max(intervals[intersect_index][1], cell.x1)

    return intervals


def further_split_row_header_cells(row_header_cells, column_intervals):
    """
    根据由表体单元格得到的初步的列区间，进一步切分行表头单元格
    :param row_header_cells: 行表头单元格
    :param column_intervals: 列区间
    :return: 进一步划分后的行表头单元格列表
    """
    # 以column_intervals为基础，对row_header_cells进行进一步分割
    split_row_header_cells = []
    for h_cell in row_header_cells:
        below_column_intervals = []
        for interval in column_intervals:
            if min(interval[1], h_cell.x1) > max(interval[0], h_cell.x0):
                below_column_intervals.append(interval)

        # 将得到的区间按照左边界升序排列
        below_column_intervals = sorted(below_column_intervals, key=lambda inter: inter[0])

        # 根据得到的区间对所有单元格进一步分割
        separate_intervals = []
        if len(below_column_intervals) > 1:
            for index in range(len(below_column_intervals) - 1):
                separate_intervals.append([below_column_intervals[index][1], below_column_intervals[index + 1][0]])

        # 对该行表头单元格进行分割
        separated_cells = split_line_by_separators(h_cell, separate_intervals)
        # 只有当分出来的单元格和每个区间都有对齐关系且分出来的单元格必须包含数字或者字母，才承认分割合法
        check = True
        if len(below_column_intervals) == len(separated_cells):
            for index in range(len(separated_cells)):
                cell1 = separated_cells[index]
                cell2 = below_column_intervals[index]
                if abs(cell1.x0 - cell2[0]) > 1 and abs(cell1.x1 - cell2[1]) > 1 and \
                        abs((cell1.x0 + cell1.x1) - (cell2[0] + cell2[1])) > 6:
                    check = False
                    break

                if cell1.get_text() == '|':
                    check = False
                    break
        if check:
            split_row_header_cells += separated_cells
        else:
            split_row_header_cells += [h_cell]

    return split_row_header_cells


def divide_cells_into_rows(cells):
    """
    对于给定的单元格，分成多行
    :param cells: 单元格列表
    :return: 单元格按行组成的列表，以及跨行的单元格列表
    """
    # 将单元格按照y0坐标进行递减排序
    sorted_cells = sorted(cells, key=lambda ce: (ce.y0 + ce.y1) / 2, reverse=True)
    rows = []
    span_row_cells = []
    for cell in sorted_cells:
        if len(rows) == 0:  # 初始状态，rows为空
            rows.append([cell])
        elif abs((cell.y0 + cell.y1) / 2 - (rows[-1][0].y0 + rows[-1][0].y1) / 2) < 1:     # 同一行
            rows[-1].append(cell)
        elif (cell.y1 - rows[-1][0].y0) / (cell.y1 - cell.y0) < 0.3:  # 新增加一行
            rows.append([cell])
        else:
            span_row_cells.append(cell)  # 跨行单元格

    return rows, span_row_cells


def handle_rows(rows, horizontal_curves):
    """
    处理按行存储的行标头单元格，包括分配父子关系
    :param rows: 按行存储的行表头单元格
    :param horizontal_curves: 页面所有的水平横线
    :return: 返回修改后的rows，并返回分行区间
    """
    # 为多行单元格分配父子关系
    for row_index in range(len(rows) - 1, 0, -1):
        current_row = rows[row_index]
        above_row = rows[row_index - 1]
        for current_cell in current_row:  # 找到和当前单元格距离最近的上层单元格作为其父亲
            minimum_distance = float('inf')
            selected_index = -1
            for above_cell_index in range(len(above_row)):
                above_cell = above_row[above_cell_index]
                # 如果上下单元格有交集，那么上面的单元格为下面单元格的父亲
                if min(above_cell.x1, current_cell.x1) > max(above_cell.x0, current_cell.x0):
                    selected_index = above_cell_index
                    break
                # 如果无交集关系，则选择最近的上行单元格作为当前单元格的夫妻
                distance = abs((above_cell.x0 + above_cell.x1) / 2 - (current_cell.x0 + current_cell.x1) / 2)
                if distance < minimum_distance:
                    minimum_distance = distance
                    selected_index = above_cell_index
            above_row[selected_index].children.append(current_cell)
            current_cell.father = above_row[selected_index]

    # 这里还需要检验父子对齐关系，待后续补充

    # 找到那些只有一个孩子且父子对齐的进行跨行融合
    for row_index in range(len(rows) - 2, -1, -1):
        for cell in rows[row_index]:
            if len(cell.children) == 1:
                # 如果父子之间有横线，不允许合并
                check = False
                for curve in horizontal_curves:
                    if cell.children[0].y0 < curve.y0 < cell.y1 and curve.x1 >= cell.x1 and curve.x0 <= cell.x0:
                        check = True
                if check:
                    continue

                child = cell.children[0]
                cell.combine(child)
                cell.children = []
                rows[row_index + 1].remove(child)
    while [] in rows:
        rows.remove([])

    # 分配行号，并记录行区间
    row_intervals = []
    for row_index in range(len(rows)):
        row = rows[row_index]
        row_intervals.append([-float('inf'), float('inf')])
        for cell in row:
            cell.start_row = row_index
            cell.end_row = row_index
            row_intervals[-1] = [max(row_intervals[-1][0], cell.y1), min(row_intervals[-1][1], cell.y0)]

    return rows, row_intervals


def handle_span_row_cells(span_row_cells, row_intervals, column_intervals):
    """
    处理跨行的行表头中的单元格，在其中加入结构信息
    :param span_row_cells: 跨行的行标头单元格
    :param row_intervals: 行表头的分行区间
    :param column_intervals: 整个表格的分列区间
    :return: 融合后的跨行单元格
    """
    # 将跨行单元格进行融合
    merge_lists = []
    for interval in column_intervals:
        merge_lists.append([])
        for cell in span_row_cells:
            find = False
            if interval[0] <= cell.x0 and interval[1] >= cell.x1:
                merge_lists[-1].append(cell)
                find = True
            if not find:
                merge_lists.insert(0, [cell])
        if len(merge_lists[-1]) == 0:
            merge_lists = merge_lists[:-1]

    span_row_cells = []
    for m_list in merge_lists:
        m_list = sorted(m_list, key=lambda ce: ce.y0, reverse=True)
        temp_cell = LTTextWordsHorizontal()
        for cell in m_list:
            temp_cell.combine(cell)
        span_row_cells.append(temp_cell)

    # 为跨行单元格分配行号
    for cell in span_row_cells:
        for interval_index in range(len(row_intervals)):
            interval = row_intervals[interval_index]
            if interval[1] <= cell.y1 <= interval[0]:
                cell.start_row = interval_index
            if interval[1] < cell.y0 < interval[0]:
                cell.end_row = interval_index

    return span_row_cells


def column_partition(table_region, initial_cells, horizontal_curves):
    """
    进行列解析
    :param table_region: 表格区域
    :param initial_cells: 初始的单元格
    :param horizontal_curves: 当前页面下所有水平线条
    :return: 行表头按行存储的单元格rows，行表头跨行单元格span_row_cells，除了行表头外的单元格split_body_cells
    """
    # ====================================================================================
    # 得到行表头，并粗略切分表头
    # 根据水平线条初步分割行表头区域和剩余区域
    row_header_cells, body_cells = separate_row_header_from_body(table_region, initial_cells, horizontal_curves)

    # 对body_cells进行初步列分割得到列区间
    column_intervals = get_column_intervals([], [], body_cells)

    # 以column_intervals为基础，对row_header_cells进行进一步分割
    row_header_cells = further_split_row_header_cells(row_header_cells, column_intervals)

    # 使用分割好的行表头单元格进一步扩大列区间
    row_header_cells = sorted(row_header_cells, key=lambda ce: ce.x1 - ce.x0)
    column_intervals = get_column_intervals(column_intervals, [], row_header_cells)

    # ====================================================================================
    # 对行表头进行详细分析
    # 对表格单元格分行
    rows, span_row_cells = divide_cells_into_rows(row_header_cells)

    # 处理rows，里面按行存放了行表头中的单元格
    rows, row_intervals = handle_rows(rows, horizontal_curves)

    # 处理span_row_cells，里面存放了跨行的单元格
    span_row_cells = handle_span_row_cells(span_row_cells, row_intervals, column_intervals)

    # ====================================================================================
    # 划分好的行表头反过来作用于列划分
    cells_without_child = []
    for row in rows:
        for cell in row:
            if len(cell.children) == 0:
                cells_without_child.append(cell)
    for cell in span_row_cells:
        cells_without_child.append(cell)
    cells_without_child = sorted(cells_without_child, key=lambda ce: ce.x0)

    # 帮助列切割
    # 对跨越两个区间的body_cells进行切割
    column_intervals = get_column_intervals([], cells_without_child, body_cells)
    column_intervals = sorted(column_intervals, key=lambda inter: inter[0])

    split_body_cells = []
    for b_cell in body_cells:
        separators = []
        for interval_index in range(len(column_intervals) - 1):
            interval = column_intervals[interval_index]
            next_interval = column_intervals[interval_index + 1]
            if b_cell.x0 < interval[1] and b_cell.x1 > next_interval[0]:
                separators.append([interval[1], next_interval[0]])
        split_cells = split_line_by_separators(b_cell, separators)
        split_body_cells += split_cells

    # 切割后若由split_body_cells得到的第一个column_intervals和第一个cells_without_child不对齐，则说明需要第一列需要进一步划分
    # 由于body_cells被切割，所以要用切割后的split_body_cells进行列区域的重新划分
    column_intervals = get_column_intervals([], cells_without_child, split_body_cells)
    column_intervals = sorted(column_intervals, key=lambda inter: inter[0])
    column_intervals_2 = get_column_intervals([], [], body_cells)
    column_intervals_2 = sorted(column_intervals_2, key=lambda inter: inter[0])
    body_cells = []
    if column_intervals_2[0][1] < column_intervals[0][0]:
        column_intervals.insert(0, column_intervals_2[0])
        for cell in split_body_cells:
            body_cells += split_line_by_separators(cell, [[column_intervals_2[0][1], column_intervals[0][0]]])
    else:
        body_cells = split_body_cells

    # 进一步切割后，再次获取列区间
    column_intervals = get_column_intervals([], cells_without_child, body_cells)
    column_intervals = sorted(column_intervals, key=lambda inter: inter[0])

    # 还需要用cells_without_child得到的column_intervals协助列融合
    merged_body_cells = []
    for interval in column_intervals:
        column_cells = []
        for cell in body_cells:
            if min(interval[1], cell.x1) > max(interval[0], cell.x0):
                column_cells.append(cell)

        column_cells = sorted(column_cells, key=lambda ce: ce.y0)
        for index in range(len(column_cells) - 1):
            current_cell = column_cells[index]
            next_cell = column_cells[index + 1]
            if abs(current_cell.y0 - next_cell.y0) < 1 and abs(current_cell.y1 - next_cell.y1) < 1:
                current_cell.combine(next_cell)
                column_cells[index + 1] = current_cell
                column_cells[index] = None

        for cell in column_cells:
            if cell is not None:
                merged_body_cells.append(cell)

    # 为所有的单元格分配列号
    for cell in merged_body_cells + span_row_cells:
        for index in range(len(column_intervals)):
            interval = column_intervals[index]
            if interval[0] <= cell.x0 <= interval[1]:
                cell.start_col = index
            if interval[0] <= cell.x1 <= interval[1]:
                cell.end_col = index
    for row in rows:
        for cell in row:
            if len(cell.children) == 0:
                for index in range(len(column_intervals)):
                    interval = column_intervals[index]
                    if interval[0] <= cell.x0 <= interval[1] and interval[0] <= cell.x1 <= interval[1]:
                        cell.start_col = index
                        cell.end_col = index
    for row in rows:  # 必须要等到子节点都分配好了开始行列，父节点才可以分配开始行列
        for cell in row:
            if len(cell.children) > 0:
                cell.start_col = cell.children[0].start_col
                cell.end_col = cell.children[-1].end_col

    return rows, span_row_cells, merged_body_cells, column_intervals
