
from semseg.table.table_utils import *

minimum_cell_number = 4  # 一个表格中应该至少包含多少个单元格
same_row_column_thres = 0.4  # 若某个线条的两个纵坐标之差小于horizontal_line_thres，则认为它是水平线条，竖直线条同理
alignment_thres = 1  # 表格的水平边界线的两个端点横坐标差值小于alignment_thres
fracture_thres = 10  # y坐标相同的线条，x坐标相差不超过fracture_thres，则将它们合并为同一根线条，对于x坐标相同的线条同理
# 表格中不允许出现的词，用于减少识别false positive
special_words = ('table', 'Table', 'TABLE')
# 算法块的标志性开头，因为算法被识别成表格的几率很高，所以单独处理
algorithm_signal = ('Algorithm', 'algorithm')


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


def exclude_algorithms(tables, algorithm_lines):
    """
    删除可能的算法框
    :param tables: 多个表格区域
    :param algorithm_lines: 含有算法标志的行
    :return: 删除后剩余的多个表格区域
    """
    remain_tables = []
    for table in tables:
        contain = False
        for element in algorithm_lines:
            element_region = [element.x0, element.y1, element.x1, element.y0]
            if relation_between_regions(table, element_region, 'CONTAIN'):
                contain = True
                break
        if not contain:
            remain_tables.append(table)
    return remain_tables


def get_cells_number(table, text_lines):
    """
    计算某个表格候选区域内的文字行的数量，用以大概估计单元格数量是否低于某个阈值
    :param table: 表格区域
    :param text_lines: 当前页面所有文字行
    :return: 区域内文字的数量
    """
    count = 0
    for line in text_lines:
        line_region = [line.x0, line.y1, line.x1, line.y0]
        if relation_between_regions(table, line_region, 'CONTAIN'):
            count += 1
    return count


def merge_curves(curves):
    """
    将排好序的断裂的线条合并
    :param curves: 页面内的所有线条
    :return: 进行线条合并后的新的线条列表
    """
    # 将线条按照x1坐标聚簇
    curve_clusters = []
    for curve in curves:
        find = False
        for cluster in curve_clusters:
            if abs(curve.x1 - cluster[0].x1) < same_row_column_thres:
                cluster.append(curve)
                find = True
                break
        if not find:
            curve_clusters.append([curve])

    merged_curves = []
    isolated_curves = []
    for cluster in curve_clusters:
        sorted_cluster_curves = sorted(cluster, key=lambda cur: cur.y1, reverse=True)
        for index in range(len(sorted_cluster_curves) - 1):
            current_y1 = sorted_cluster_curves[index].y1
            current_y0 = sorted_cluster_curves[index].y0
            next_y1 = sorted_cluster_curves[index + 1].y1
            next_y0 = sorted_cluster_curves[index + 1].y0
            if current_y0 - next_y1 < fracture_thres:
                sorted_cluster_curves[index + 1].y1 = current_y1
                sorted_cluster_curves[index + 1].y0 = min(current_y0, next_y0)
                sorted_cluster_curves[index] = None

        if sorted_cluster_curves[0] is not None:
            isolated_curves.append(sorted_cluster_curves[0])
        for index in range(1, len(sorted_cluster_curves)):
            if sorted_cluster_curves[index] is not None:
                if sorted_cluster_curves[index - 1] is None:
                    merged_curves.append(sorted_cluster_curves[index])
                else:
                    isolated_curves.append(sorted_cluster_curves[index])

    return merged_curves, isolated_curves


def find_cells_in_region(region, text_lines):
    """
    找到指定区域内的所有文字航
    :param region: 制定区域
    :param text_lines: 当前页面的所有文字行
    :return: 指定区域内的所有文字行
    """
    res = []
    for line in text_lines:
        line_region = [line.x0, line.y1, line.x1, line.y0]
        if relation_between_regions(region, line_region, 'CONTAIN'):
            res.append(line)

    return res


def extend_table_region(regions, vertical_curves, fake_vertical_curves, text_lines):
    """
    通过竖直线条进一步扩大表格范围
    :param regions: 初始的表格范围
    :param vertical_curves: 竖直线条
    :param fake_vertical_curves: 空白分隔符
    :param text_lines: 当前页面的所有文字行
    :return: 扩大后的表格范围
    """
    extended_tables = []
    for region in regions:
        related_vertical_curves = []

        # 处理fake_vertical_curves
        for curve in fake_vertical_curves:
            if region[0] < curve.x0 < region[2] and \
                    (min(curve.y1, region[1]) - max(curve.y0, region[3])) / (curve.y1 - curve.y0) > 0.5:
                related_vertical_curves.append(curve)

        # 处理vertical_curves
        for curve in vertical_curves:
            if region[0] < curve.x0 < region[2] and min(curve.y1, region[1]) - max(curve.y0, region[3]) > -0.3:
                related_vertical_curves.append(curve)

        extended_region = region.copy()
        for curve in related_vertical_curves:
            extended_region = [extended_region[0], max(extended_region[1], curve.y1), extended_region[2],
                               min(extended_region[3], curve.y0)]

        # 如果通过扩展使得整个表格只增加了一个文字行，则不承认此次扩展
        pre_text_lines = find_cells_in_region(region, text_lines)
        pro_text_lines = find_cells_in_region(extended_region, text_lines)
        if len(pro_text_lines) - len(pre_text_lines) <= 1:
            extended_tables.append(region)
        else:
            extended_tables.append(extended_region)
    return extended_tables


def get_fake_vertical_curves(text_lines):
    """
    通过对齐方式找到竖直方向的虚拟线条
    :param text_lines: 当前页面内的所有文字行
    :return: 所有虚拟竖直线条
    """
    # 将所有的文字行分别按照左对齐、右对齐、居中对齐的方法聚成簇
    left_fake_curves = []
    right_fake_curves = []
    mid_fake_curves = []
    for line in text_lines:
        left_fake_curves.append(LTCurve(same_row_column_thres, [(line.x0, line.y1), (line.x0, line.y0)]))
        right_fake_curves.append(LTCurve(same_row_column_thres, [(line.x1, line.y1), (line.x1, line.y0)]))
        mid_fake_curves.append(LTCurve(same_row_column_thres,
                                       [((line.x0 + line.x1) / 2, line.y1), ((line.x0 + line.x1) / 2, line.y0)]))
    left_fake_curves, _ = merge_curves(left_fake_curves)
    right_fake_curves, _ = merge_curves(right_fake_curves)
    mid_fake_curves, _ = merge_curves(mid_fake_curves)

    return left_fake_curves + right_fake_curves + mid_fake_curves


def detect_tables_with_single_horizontal_line(isolated_horizontal_curves, vertical_curves, fake_vertical_curves):
    """
    检测仅有一个水平线条的表格
    :param isolated_horizontal_curves: 孤立的水平线条列表
    :param vertical_curves: 页面内所有的竖直线条
    :param fake_vertical_curves: 虚拟竖直线条
    :return: 表格列表，格式为[[table.x0, table.y1, table.x1, table.y0], ...]
    """
    tables = []
    for h_curve in isolated_horizontal_curves:
        intersect_curves = []
        for v_curve in fake_vertical_curves:
            if h_curve.x0 <= v_curve.x0 <= h_curve.x1 and v_curve.y0 < h_curve.y0 < v_curve.y1:
                intersect_curves.append(v_curve)
        intersect_curves = sorted(intersect_curves, key=lambda cur: cur.x0)
        for v_curve in vertical_curves:
            if h_curve.x0 < v_curve.x0 < h_curve.x1 and v_curve.y0 < h_curve.y0 < v_curve.y1:
                intersect_curves.append(v_curve)

        if len(intersect_curves) > 0:
            table = [h_curve.x0, -float('inf'), h_curve.x1, float('inf')]
            for v_curve in intersect_curves:
                table[1] = max(table[1], v_curve.y1)
                table[3] = min(table[3], v_curve.y0)

            tables.append(table)

    return tables


def detect_table_with_horizontal_lines(regions, algorithm_lines, vertical_curves, fake_vertical_curves, text_lines):
    """
    检测出含有多条水平线条的表格
    :param regions: 可能的表格区域
    :param algorithm_lines: 含有算法字样的文字行
    :param vertical_curves: 当前页面内的竖直线条
    :param fake_vertical_curves: 当前页面内的虚拟竖直线条
    :param text_lines: 当前页面下的所有文字行
    :return:
    """
    # 去除算法块
    regions_without_algorithm_lines = exclude_algorithms(regions, algorithm_lines)

    # 利用竖直线条对表格范围进行进一步扩展
    extended_regions = extend_table_region(regions_without_algorithm_lines, vertical_curves, fake_vertical_curves,
                                           text_lines)

    return extended_regions


def detetct_singal_column(sorted_curves, elements_dict):
    """
    检测出单栏中的所有表格
    :param sorted_curves: 按照ｙ降序排列的本栏中的所有横线
    :param elements_dict: 页面中其他元素成分组成的词典
    """
    # 将词典中的各成分提取出来
    vertical_curves = elements_dict['vertical_curves']
    fake_vertical_curves = elements_dict['fake_vertical_curves']
    text_lines = elements_dict['text_lines']
    special_lines = []
    algorithm_lines = []
    for line in text_lines:
        if line.get_text().lower().startswith(special_words):
            special_lines.append(line)
        if line.get_text().startswith(algorithm_signal):
            algorithm_lines.append(line)

    # 将排好序的线条初步分组，每一组为一个表格区域的候选者
    initial_groups = divide_curves_into_groups(sorted_curves, special_lines)

    # 大多数表格线条水平线条数量大于１，少数表格水平线条数量等于１，分开处理
    regions = []
    isolated_horizontal_curves = []
    for group in initial_groups:
        if len(group) > 1:
            regions.append([group[0].x0, group[0].y0, group[-1].x1, group[-1].y1])
        elif len(group) == 1:
            isolated_horizontal_curves.append(group[0])

    # 对两种情况分开检测表格区域
    t1 = detect_table_with_horizontal_lines(regions, algorithm_lines, vertical_curves, fake_vertical_curves, text_lines)
    t2 = detect_tables_with_single_horizontal_line(isolated_horizontal_curves, vertical_curves, fake_vertical_curves)
    tables = t1 + t2

    # 表格内的文字行必须大于等于4
    selected_tables = []
    for table in tables:
        if get_cells_number(table, text_lines) >= 4:
            selected_tables.append(table)

    return selected_tables


def detect_table(page_layout):
    """
    检测给定页面的所有表格
    :param page_layout: 由于pdfminer解析得到的布局信息
    :return: 当前页面的所有表格区域，格式为[[左上x, 左上y, 右下x, 右下y], ...]
    """
    # 从布局信息中提取可能需要用的box，水平横线、文字行、以为特殊字段开头的行
    horizontal_curves = get_horizontal_curves(page_layout)
    vertical_curves, isolated_curves = merge_curves(get_vertical_curves(page_layout))
    vertical_curves += isolated_curves
    text_lines = get_text_lines(page_layout)
    fake_vertical_curves = get_fake_vertical_curves(text_lines)

    # 将所有需要使用到的不同类别（除线条外）的页面元素放入字典中，使得参数列表更加清晰
    elements_dict = {
        'vertical_curves': vertical_curves,
        'fake_vertical_curves': fake_vertical_curves,
        'text_lines': text_lines,
    }

    # 将所有线条按照y坐标降序排列，便于后续操作
    sorted_curves = sorted(horizontal_curves, key=lambda cur: cur.y0, reverse=True)

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

    # 上述的解决两栏版面带来的问题，可能出现表格过度切分，所以将大表格内套小表格的情况消除
    tables = left_tables + right_tables
    for front in range(len(tables) - 1):
        for behind in range(front+1, len(tables)):
            if relation_between_regions(tables[front], tables[behind], 'CONTAIN'):
                tables[behind] = tables[front]
                tables[front] = None
                break
            elif relation_between_regions(tables[behind], tables[front], 'CONTAIN'):
                tables[front] = None
                break
    while None in tables:
        tables.remove(None)

    return tables
