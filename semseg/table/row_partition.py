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


def row_partition(initial_cells, horizontal_curves, column_intervals):
    """

    :param initial_cells:
    :param horizontal_curves:
    :return:
    """
    # # 若只有一列，那么必定为全线条表格
    # if len(column_intervals) == 1:


    # 用横线缩小切分单元格的高度
    for cell in initial_cells:
        for curve in horizontal_curves:
            if cell.y0 < curve.y0 < cell.y1 and \
                    min(cell.x1, curve.x1) - max(cell.x0, curve.x0) > 0.5 * (cell.x1 - cell.x0):
                if curve.y0 > (cell.y0 + cell.y1) / 2:
                    cell.y1 = curve.y0 - 0.1
                else:
                    cell.y0 = curve.y0 + 0.1

    # 对于位于同一列的单元格，如果有两个单元格重叠，则切分开来
    groups = []  # 先将单元格按列分组
    span_column_cells = []
    for interval in column_intervals:
        groups.append([])
    for cell in initial_cells:
        find = False
        for index in range(len(column_intervals)):
            interval = column_intervals[index]
            if min(cell.x1, interval[1]) - max(cell.x0, interval[0]) > 0.8 * (cell.x1 - cell.x0):
                groups[index].append(cell)
                find = True
                break
        if not find:
            span_column_cells.append(cell)

    for group in groups:
        group = sorted(group, key=lambda ce: ce.y0 + ce.y1, reverse=True)
        for index in range(len(group) - 1):
            current_cell = group[index]
            below_cell = group[index + 1]
            if current_cell.y0 < below_cell.y1:
                below_cell.y1 = current_cell.y0

    # 默认第一列为行表头
    row_header_cells = []
    for cell in groups[0]:
        row_header_cells.append(cell)

    body_cells = []
    groups = groups[1:]
    for group in groups:
        for cell in group:
            body_cells.append(cell)
    for cell in span_column_cells:
        body_cells.append(cell)

    # 根据行表头划分行区间
    row_intervals = get_row_intervals(row_header_cells, body_cells)
    row_intervals = sorted(row_intervals, key=lambda inter: inter[0], reverse=True)

    # 分配行号
    for cell in row_header_cells + body_cells:
        for index in range(len(row_intervals)):
            interval = row_intervals[index]
            find = False
            if (min(cell.y1, interval[0]) - max(cell.y0, interval[1])) > 0.8 * (cell.y1 - cell.y0):
                cell.start_row = index
                cell.end_row = index
                find = True

        if not find:
            for index in range(len(row_intervals)):
                interval = row_intervals[index]
                if interval[1] <= cell.y1 <= interval[0]:
                    cell.start_row = index
                if interval[1] <= cell.y0 <= interval[0]:
                    cell.end_row = index

    return row_header_cells, body_cells, row_intervals
