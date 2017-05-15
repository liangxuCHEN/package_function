# encoding=utf8

import copy
from package_tools import use_rate, draw_one_pic, can_merge_place, tidy_shape

"""
基于V3上的优化
给定数量的产品，求混排的最优结果
输出板材的数量和排版结果
"""


def tidy_empty_place(em_place):
    """
    整理剩余的空间，尽量把能够合并的空间都合并成一个大的剩余空间，
    然后按照空间的坐标排序，从下往上，从左到右
    :param em_place:
    :return:
    """
    index_place = 0
    while index_place < len(em_place):
        for place in em_place:
            if em_place.index(place) != index_place:
                can_merge, new_place = can_merge_place(place, em_place[index_place])
                if can_merge:
                    em_place.pop(index_place)
                    em_place.remove(place)
                    em_place.append(new_place)
                    index_place = 0
                    break
        index_place += 1

    for i in range(len(em_place) - 1, 0, -1):
        for j in range(0, i):
            # 比较Y的开始值
            if em_place[j][1] > em_place[j + 1][1]:
                em_place[j], em_place[j + 1] = em_place[j + 1], em_place[j]
            elif em_place[j][1] == em_place[j + 1][1] and em_place[j][0] > em_place[j + 1][0]:
                em_place[j], em_place[j + 1] = em_place[j + 1], em_place[j]

    return em_place


def update_empty_place(solution, shape_x, shape_y, num_shape, border):
    """
    根据solution的排列方案，确定每一个矩形的位置
    :param solution: 矩形排列方案
    :param shape_x: 矩形的边长
    :param shape_y: 矩形的边长
    :param num_shape:需要排列矩形的数量
    :param border: 矩形间的间隙
    :return:
    res：一个队列，包含排列好的矩形的坐标
    end_point: None：排列的矩形数量少于需要排序的数量
     填入数量超过图形的总数num_shape，返回一个字典：
     2种模式： 1:整齐的(tidy): 在一个循环刚好排好图形，记录剩下空间节点
               2：不整齐(no_tidy): 在中途退出循环，记录退出的节点
        {
            'model': tidy or no_tidy,
            'point': (x0, y0, x1, y1)
        }
    """
    res = list()
    end_point = {}  # 四个坐标点, 2种模式： 1:整齐的，2：不整齐
    # 添加放置位置, 填入数量不要超过图形的总数num_shape
    if solution['model'] == 'w':
        # 第一种情况
        total_h = solution['place'][1] + shape_y
        while solution['place'][3] >= total_h and len(res) <= num_shape:
            for i in range(0, solution['x']):
                res.append(
                    (solution['place'][0] + i * shape_x + i * border,
                     total_h - shape_y,
                     shape_x, shape_y)
                )
                # 在循环中已经完成排列,中途退出,记录退出点
                if len(res) > num_shape:
                    # 不包含间隔
                    end_point['point'] = (
                        solution['place'][0] + i * shape_x + i * border,
                        total_h - shape_y,
                        solution['place'][0] + (i + 1) * shape_x + i * border,
                        total_h,
                    )
                    end_point['model'] = 'no_tidy'
                    res.pop()
                    return res, end_point

            total_h += shape_y + border

        # 选择90度矩形继续摆放
        begin_x = solution['place'][0] + solution['x'] * shape_x + solution['x'] * border
        # 在一个循环刚好满足的情况，记录剩余空间
        if len(res) == num_shape and solution['place'][3] >= total_h:
            end_point['point'] = (
                solution['place'][0],
                total_h - shape_x,
                begin_x,
                solution['place'][3],
            )
            end_point['model'] = 'tidy'
            return res, end_point

        # 第二种情况
        total_h = solution['place'][1] + shape_x
        while solution['place'][3] >= total_h and len(res) <= num_shape:
            for i in range(0, solution['y']):
                res.append(
                    (begin_x + i * shape_y + i * border,
                     total_h - shape_x,
                     shape_y, shape_x)
                )
                # 在循环中已经完成排列,中途退出,记录退出点
                if len(res) > num_shape:
                    end_point['point'] = (
                        begin_x + i * shape_y + i * border,
                        total_h - shape_x,
                        begin_x + (i + 1) * shape_y + i * border,
                        total_h,
                    )
                    end_point['model'] = 'no_tidy'
                    res.pop()
                    return res, end_point
            total_h += shape_x + border

        # 在一个循环刚好满足的情况，记录剩余空间
        if len(res) == num_shape and solution['place'][3] >= total_h:
            end_point['point'] = (
                begin_x,
                total_h - shape_x,
                solution['place'][2],
                solution['place'][3],
            )
            end_point['model'] = 'tidy'

    else:
        # 竖直方向
        # 第一种情况
        total_w = solution['place'][0] + shape_y
        while solution['place'][2] >= total_w and len(res) <= num_shape:
            for i in range(0, solution['x']):
                res.append(
                    (total_w - shape_y,
                     solution['place'][1] + i * shape_x + i * border,
                     shape_y, shape_x)
                )
                # 在循环中已经完成排列,中途退出,记录退出点
                if len(res) > num_shape:
                    end_point['point'] = (
                        total_w - shape_y,
                        solution['place'][1] + i * shape_x + i * border,
                        total_w,
                        solution['place'][1] + (i + 1) * shape_x + i * border,
                    )
                    end_point['model'] = 'no_tidy'
                    res.pop()
                    return res, end_point
            total_w += shape_y + border

        begin_y = solution['place'][1] + solution['x'] * shape_x + solution['x'] * border
        # 在一个循环刚好满足的情况, 记录剩余空间
        if len(res) == num_shape and solution['place'][2] >= total_w:
            end_point['point'] = (
                total_w - shape_y,
                solution['place'][1],
                solution['place'][2],
                begin_y,
            )
            end_point['model'] = 'tidy'
            return res, end_point

        # 第二种情况
        total_w = solution['place'][0] + shape_x
        while solution['place'][2] >= total_w and len(res) <= num_shape:
            for i in range(0, solution['y']):
                res.append(
                    (total_w - shape_x,
                     begin_y + i * shape_y + i * border,
                     shape_x, shape_y)
                )
                # 在循环中已经完成排列,中途退出,记录退出点
                if len(res) > num_shape:
                    end_point['point'] = (
                        total_w - shape_x,
                        begin_y + i * shape_y + i * border,
                        total_w,
                        begin_y + (i + 1) * shape_y + i * border,
                    )
                    end_point['model'] = 'no_tidy'
                    res.pop()
                    return res, end_point
            total_w += shape_x + border

        # 在一个循环刚好满足的情况, 记录剩余空间
        if len(res) == num_shape and solution['place'][2] >= total_w:
            end_point['point'] = (
                total_w - shape_x,
                begin_y,
                solution['place'][2],
                solution['place'][3],
            )
            end_point['model'] = 'tidy'

    return res, end_point


def cal_rate_num(shape_x, shape_y, length, other, border):
    """
    根据矩形的边长和空间的大小，寻找合适的排列方案
    :param shape_x: 矩形的边长
    :param shape_y: 矩形的边长
    :param length: 空间边长，这次计算的边长
    :param other: 空间另外一个边长
    :param border: 图形的间隙
    :return:
    solution : 排列方案，在这条边上
    {
    'x': 1    x 边长 排多少个
    'y': 3    y 边长 排多少个
    'empty': 根据这个方案，得到的剩余空间面积
    }
    """
    max_x = int(length + border) / int((shape_x + border))
    max_y = int(length + border) / int((shape_y + border))
    tmp_solution = {
        'y': 0,
        'x': 0,
        'empty': length * other,  # 最小空白地方，初始值为整个
    }
    for i in range(0, max_x + 1):
        for j in range(0, max_y + 1):
            # 求组合的最小空余地方
            tmp_length = i * shape_x + j * shape_y + (i + j - 1) * border
            if length - tmp_length >= 0:
                tmp_other_len = int(other + border) % int(shape_y + border)
                total_empty_area = tmp_other_len * (i * shape_x + (i - 1) * border)
                tmp_other_len = int(other + border) % int(shape_x + border)
                total_empty_area += tmp_other_len * (j * shape_y + (j - 1) * border)
                total_empty_area += (length - tmp_length) * other
                if tmp_solution['empty'] > total_empty_area:
                    tmp_solution['y'] = j
                    tmp_solution['x'] = i
                    tmp_solution['empty'] = total_empty_area

    return tmp_solution


def find_model(shape_x, shape_y, place, border):
    """
    拆分矩形,找适合的矩形, place坐标表示空余空间:(0,0,30,40) = begin(0,0), end(30,40)
    判断怎么放，横竖组合，然后看剩余多少，找出剩余空间最少的方案
    :param shape_x: 矩形边长
    :param shape_y: 矩形边长
    :param place: 空余空间
    :param border: 图形间间隙
    :return:
    solution: 排列的方案
    {
    'x': 1    x 边长 排多少个
    'y': 3    y 边长 排多少个
    'empty': 根据这个方案，得到的剩余空间面积
    'model': 根据空间的长或者宽的边来排列 w：长边排列，h：宽边排列
    'length': 选取空间的边的长度
    'place': 空间的坐标
    }
    """
    # 初始化空白可填充部分
    width = place[2] - place[0]
    height = place[3] - place[1]
    # 先找出两种模式的最佳解
    solution_1 = cal_rate_num(shape_x, shape_y, width, height, border)
    solution_1['model'] = 'w'
    solution_1['place'] = place
    solution_2 = cal_rate_num(shape_x, shape_y, height, width, border)
    solution_2['model'] = 'h'
    solution_2['place'] = place
    # 比较两种模式，找出最优解
    if solution_1['empty'] > solution_2['empty']:
        if solution_2['model'] == 'w':
            solution_2['length'] = height
        else:
            solution_2['length'] = width
        return solution_2
    else:
        if solution_1['model'] == 'w':
            solution_1['length'] = height
        else:
            solution_1['length'] = width
        return solution_1


def is_valid_point(place, width, height):
    """
    判断计算出来的坐标是否合理
    :param place:
    :param width:
    :param height:
    :return:
    """
    place = list(place)
    if place[2] > width:
        place[2] = width
    if place[3] > height:
        place[3] = height
    if place[0] >= place[2] or place[1] >= place[3]:
        return False, None
    return True, tuple(place)


def find_empty_place(shape_x, shape_y, solution, end_point, border, width, height):
    """
    根据排列方案，找到新的空余的空间
    :param shape_x: 矩形的边
    :param shape_y: 矩形的边
    :param solution: 排列方案
    :param end_point: 中途停止，因为已经把所有的图形放好了，记录的退出坐标点
    模式一：整齐的(tidy): 在一个循环刚好排好图形，剩余空间节点
    模式二：不整齐(no_tidy): 在中途退出循环，记录退出的节点
    :param border: 图形间的间隙
    :return:
    split_list : 分割线的坐标
    empty_list : 新的空余空间
    """
    # 初始化参数
    model = None
    if 'model' in end_point.keys():
        model = end_point['model']
    if 'point' in end_point.keys():
        end_point = end_point['point']
    else:
        end_point = None
    empty_list = list()
    split_list = list()

    if solution['model'] == 'w':
        # 水平模式
        # 计算分割线
        split_list.append((
            solution['place'][0],
            solution['place'][1],
            solution['place'][0] + solution['x'] * shape_x + border * (solution['x'] - 1),
            solution['place'][3]
        ))
        split_list.append((
            solution['place'][0] + solution['x'] * shape_x + border * solution['x'],
            solution['place'][1],
            solution['place'][2],
            solution['place'][3]
        ))
        # 是否有结束的点，没有代表这块空间排放的矩形数量少于需要排放的空间
        if end_point is None:
            if solution['x'] > 0:
                is_valid, em_place = is_valid_point((
                    solution['place'][0],
                    solution['place'][3] - int(solution['length'] + border) % int(shape_y + border) + border,
                    solution['place'][0] + solution['x'] * shape_x + (solution['x'] - 1) * border,
                    solution['place'][3]
                ), width, height)
                if is_valid:
                    empty_list.append(em_place)

            if solution['y'] > 0:
                is_valid, em_place = is_valid_point((
                    solution['place'][0] + solution['x'] * shape_x + border * solution['x'],
                    solution['place'][3] - int(solution['length'] + border) % int(shape_x + border) + border,
                    solution['place'][0] + solution['x'] * shape_x + solution['y'] * shape_y + (
                        solution['x'] + solution['y'] - 1) * border,
                    solution['place'][3]
                ), width, height)
                if is_valid:
                    empty_list.append(em_place)

            is_valid, em_place = is_valid_point((
                solution['place'][0] + (solution['y'] * shape_y + solution['x'] * shape_x + (
                    solution['y'] + solution['x'] - 1) * border) + border,
                solution['place'][1],
                solution['place'][2],
                solution['place'][3],
            ), width, height)
            if is_valid:
                empty_list.append(em_place)
        else:
            # 有结束点的情况，其中no_tidy 表示结束点在一行或一列之间
            if model == 'no_tidy':
                if end_point[0] < solution['place'][0] + solution['x'] * shape_x + border * solution['x']:
                    # 另一边是空的
                    is_valid, em_place = is_valid_point((
                        solution['place'][0] + solution['x'] * shape_x + border * solution['x'],
                        solution['place'][1],
                        solution['place'][2],
                        solution['place'][3],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)

                    # 有东西的一边,结束那一部分
                    is_valid, em_place = is_valid_point((
                        end_point[0],
                        end_point[1],
                        solution['place'][0] + solution['x'] * shape_x + border * solution['x'],
                        solution['place'][3],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)

                    # 有东西的一边, 前面排好部分
                    if solution['x'] > 0:
                        is_valid, em_place = is_valid_point((
                            solution['place'][0],
                            end_point[3] + border,
                            end_point[0],
                            solution['place'][3]
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                else:
                    # 一边放满的
                    if solution['x'] > 0:
                        is_valid, em_place = is_valid_point((
                            solution['place'][0],
                            solution['place'][3] - int(solution['length'] + border) % int(shape_y + border) + border,
                            solution['place'][0] + solution['x'] * shape_x + (solution['x'] - 1) * border,
                            solution['place'][3]
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                    # 另一边没有放满的
                    # TODO : 只有一列的情况
                    if solution['y'] > 0:
                        is_valid, em_place = is_valid_point((
                            solution['place'][0] + solution['x'] * shape_x + border * solution['x'],
                            end_point[3] + border,
                            solution['place'][2],
                            solution['place'][3]
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                        # 里面没有用的空间不需要加间隙
                        is_valid, em_place = is_valid_point((
                            end_point[0],
                            end_point[1],
                            solution['place'][2],
                            end_point[3] + border
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                    # 最边没有利用的地方， 外面算要加间隙
                    is_valid, em_place = is_valid_point((
                        solution['place'][0] + (solution['y'] * shape_y + solution['x'] * shape_x + (
                            solution['y'] + solution['x']) * border),
                        solution['place'][1],
                        solution['place'][2],
                        end_point[1],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)
            else:
                # 排放的图形刚好整齐在一行或一列结束
                if end_point[0] < solution['place'][0] + solution['x'] * shape_x + border * solution['x']:
                    # 另一边是空的
                    is_valid, em_place = is_valid_point((
                        solution['place'][0] + solution['x'] * shape_x + border * solution['x'],
                        solution['place'][1],
                        solution['place'][2],
                        solution['place'][3],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)

                    is_valid, em_place = is_valid_point(end_point, width, height)
                    if is_valid:
                        empty_list.append(em_place)
                else:
                    if solution['x'] > 0:
                        is_valid, em_place = is_valid_point((
                            solution['place'][0],
                            solution['place'][3] - int(solution['length'] + border) % int(shape_y + border) + border,
                            solution['place'][0] + solution['x'] * shape_x + (solution['x'] - 1) * border,
                            solution['place'][3]
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                    if solution['y'] > 0:
                        # 边框剩下
                        is_valid, em_place = is_valid_point((
                            solution['place'][0] + solution['x'] * shape_x + solution['y'] * shape_y + (
                                solution['x'] + solution['y']) * border,
                            solution['place'][1],
                            solution['place'][2],
                            solution['place'][3]
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                    is_valid, em_place = is_valid_point(end_point, width, height)
                    if is_valid:
                        empty_list.append(em_place)

    else:
        # 竖直模式
        # 计算分割线
        split_list.append((
            solution['place'][0],
            solution['place'][1],
            solution['place'][2],
            solution['place'][1] + solution['x'] * shape_x + border * (solution['x'] - 1)
        ))
        split_list.append((
            solution['place'][0],
            solution['place'][1] + solution['x'] * shape_x + border * solution['x'],
            solution['place'][2],
            solution['place'][3]
        ))
        # 是否有结束点
        if end_point is None:
            if solution['x'] > 0:
                is_valid, em_place = is_valid_point((
                    solution['place'][2] - int(solution['length'] + border) % int(shape_y + border) + border,
                    solution['place'][1],
                    solution['place'][2],
                    solution['place'][1] + solution['x'] * shape_x + (solution['x'] - 1) * border
                ), width, height)
                if is_valid:
                    empty_list.append(em_place)

            if solution['y'] > 0:
                is_valid, em_place = is_valid_point((
                    solution['place'][2] - int(solution['length'] + border) % int(shape_x + border) + border,
                    solution['place'][1] + solution['x'] * shape_x + border * solution['x'],
                    solution['place'][2],
                    solution['place'][1] + solution['x'] * shape_x + solution['y'] * shape_y + (
                        solution['y'] + solution['x'] - 1) * border
                ), width, height)
                if is_valid:
                    empty_list.append(em_place)

            is_valid, em_place = is_valid_point((
                solution['place'][0],
                solution['place'][1] + (solution['y'] * shape_y + solution['x'] * shape_x + (
                    solution['y'] + solution['x'] - 1) * border) + border,
                solution['place'][2],
                solution['place'][3],
            ), width, height)
            if is_valid:
                empty_list.append(em_place)

        else:
            # 有结束点， 在一行或一列之间
            if model == 'no_tidy':
                if end_point[1] < solution['place'][1] + solution['x'] * shape_x + border * solution['x']:
                    # 另一边是空的
                    is_valid, em_place = is_valid_point((
                        solution['place'][0],
                        solution['place'][1] + solution['x'] * shape_x + border * solution['x'],
                        solution['place'][2],
                        solution['place'][3],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)

                    # 有东西的一边
                    is_valid, em_place = is_valid_point((
                        end_point[0],
                        end_point[1],
                        solution['place'][2],
                        solution['place'][1] + solution['x'] * shape_x + border * solution['x'],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)

                    # 有东西的一边, 前面排好部分
                    is_valid, em_place = is_valid_point((
                        end_point[2] + border,
                        solution['place'][1],
                        solution['place'][2],
                        end_point[1],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)
                else:
                    # 还没有放完的空间
                    is_valid, em_place = is_valid_point((
                        end_point[0],
                        end_point[1],
                        solution['place'][2],
                        solution['place'][3],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)

                    # 已经放东西后还剩余的地方
                    if solution['x'] > 0:
                        is_valid, em_place = is_valid_point((
                            solution['place'][2] - int(solution['length'] + border) % int(shape_y + border) + border,
                            solution['place'][1],
                            solution['place'][2],
                            solution['place'][1] + solution['x'] * shape_x + (solution['x'] - 1) * border
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                    if solution['y'] > 0:
                        is_valid, em_place = is_valid_point((
                            end_point[2] + border,
                            solution['place'][1] + solution['x'] * shape_x + border * solution['x'],
                            solution['place'][2],
                            end_point[1] - border,
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                        # 已经放置的顶部部分
                        is_valid, em_place = is_valid_point((
                            solution['place'][0],
                            end_point[3] + border,
                            end_point[0],
                            solution['place'][3]
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)
            else:
                # 整齐的一行或一列的情况
                if end_point[1] < solution['place'][1] + solution['x'] * shape_x + border * solution['x']:
                    # 另一边是空的
                    is_valid, em_place = is_valid_point((
                        solution['place'][0],
                        solution['place'][1] + solution['x'] * shape_x + border * solution['x'],
                        solution['place'][2],
                        solution['place'][3],
                    ), width, height)
                    if is_valid:
                        empty_list.append(em_place)

                    # 有东西的一边
                    is_valid, em_place = is_valid_point(end_point, width, height)
                    if is_valid:
                        empty_list.append(em_place)
                else:
                    # 已经放东西后还剩余的地方
                    if solution['x'] > 0:
                        is_valid, em_place = is_valid_point((
                            solution['place'][2] - int(solution['length'] + border) % int(shape_y + border) + border,
                            solution['place'][1],
                            solution['place'][2],
                            solution['place'][1] + solution['x'] * shape_x + solution['x'] * border
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)

                    # 有东西的一边
                    if solution['y'] > 0:
                        # 边框剩下
                        is_valid, em_place = is_valid_point((
                            solution['place'][0],
                            solution['place'][1] + (solution['y'] * shape_y + solution['x'] * shape_x + (
                                solution['y'] + solution['x'] - 1) * border) + border,
                            end_point[0],
                            solution['place'][3],
                        ), width, height)
                        if is_valid:
                            empty_list.append(em_place)
                    # 剩余
                    is_valid, em_place = is_valid_point(end_point, width, height)
                    if is_valid:
                        empty_list.append(em_place)

    return split_list, empty_list


def find_one_best(shape_x, shape_y, place, num_shape, texture, border, width, height):
    """
    找单个图形的最大利用率
    :param shape_x: 矩形的边
    :param shape_y: 矩形的边
    :param place: 空余地方
    :param num_shape: 需要安放的数量
    :param texture: 是否有纹理
    :param border: 图形间的间隙
    :return:
    situation: 矩形的排列坐标
    empty_place: 剩余的空间列表
    """
    if texture == 0:
        # 没有纹理
        solution = find_model(shape_x, shape_y, place, border)
    else:
        # 有纹理的，单方向，解决方案变成唯一
        width = place[2] - place[0]
        height = place[3] - place[1]
        solution = {
            'y': 0,
            'x': int(width + border) / int((shape_x + border)),
            'empty': width * height,  # 最小空白地方，初始值为整个
            'model': 'w',
            'place': place,
            'length': height,
        }

    # 更新空余地方，还需要根据已经排列的图形，再计算
    situation, end_point = update_empty_place(solution, shape_x, shape_y, num_shape, border)
    split_place, empty_place = find_empty_place(shape_x, shape_y, solution, end_point, border, width, height)
    while True and len(situation) < num_shape and texture == 0:
        # 再次判断，找更好的情况
        tmp_situation = list()
        tmp_split_place = list()
        tmp_empty_place = list()
        for e_place in split_place:
            solution = find_model(shape_x, shape_y, e_place, border)
            sub_tmp_situation, end_point = update_empty_place(solution, shape_x, shape_y, num_shape, border)
            tmp_situation += sub_tmp_situation
            res = find_empty_place(shape_x, shape_y, solution, end_point, border, width, height)
            tmp_split_place += res[0]
            tmp_empty_place += res[1]

        # 有更好的情况，就更新
        if len(tmp_situation) > len(situation):
            situation = copy.deepcopy(tmp_situation)
            split_place = copy.deepcopy(tmp_split_place)
            empty_place = copy.deepcopy(tmp_empty_place)
        else:
            break

    return situation, empty_place


def get_shape_data(data, width, num_pic=1):
    """
    输入是一个字符串如：400 500 30;130 250 10;800 900 5;
    没有空格，然后通过处理，返回两个队列

    :param data:
    :return:
    shape_list: [(400,500), (130,250),(900,800)]  一个矩形的长宽
    shape_num: [30,10,5] 对应矩形的数量
    """
    shape_list = list()
    shape_num = list()
    shapes = data.split(';')
    for shape in shapes:
        try:
            x, y, num = shape.split(' ')
            x = int(x)
            y = int(y)
            num = int(num) * num_pic
            shape_list.append((x, y))
            shape_num.append(num)
        except:
            return {
                'error': True,
                'info': u'输入的格式不对, 一组数据之间用空格, 数据之间用分号<;>, 最后结尾不要放分号<;>, 而且要用英文标点'
            }
        if x > width or y > width:
            return {'error': True, 'info': u'输入尺寸数值错误，组件尺寸必须小于板材'}
        if x <= 0 or y <= 0:
            return {'error': True, 'info': u'输入尺寸数值错误，尺寸输入值必须大于零'}
        if num <= 0:
            return {'error': True, 'info': u'输入矩形数量错误，输入值必须大于零'}

    return {'shape_list': shape_list, 'shape_num': shape_num, 'error': False}


def main_process(data, pathname):
    """
    给出矩形的大小和数量，以及板材的尺寸，返回需要多少块板材，以及每一块板材的利用率
    :param data: 所有输入数据
    :param pathname: 输出排列的数据的文档路径
    :return:
    reslut: [0.9, 0.88,,0.78] 返回每块板的利用率
    """
    # 输入值合理性判断
    try:
        # 板材尺寸
        WIDTH = int(data['width'])
        HEIGHT = int(data['height'])
        BORDER = float(data['border'])    # 间隙
    except ValueError:
        return {'error': True, 'info': u'输入类型错误，输入值必须是数值类型'}

    if WIDTH <= 0 or HEIGHT <= 0:
        return {'error': True, 'info': u'输入尺寸数值错误，尺寸输入值必须大于零'}
    # 防止输入长宽位置错，自动调整
    if WIDTH < HEIGHT:
        WIDTH, HEIGHT = HEIGHT, WIDTH

    if BORDER < 0:
        return {'error': True, 'info': u'输入尺寸数值错误，组件间隙不能小于零'}

    # 矩形参数
    shape_result = get_shape_data(data['shape_data'], WIDTH)
    if shape_result['error']:
        return {'error': True, 'info': shape_result['info']}
    else:
        SHAPE = shape_result['shape_list']
        SHAPE_NUM = shape_result['shape_num']

    is_texture = int(data['is_texture'])    # 是否有纹理，有纹理不能旋转 0：没有， 1：有
    is_vertical = int(data['is_vertical'])  # 当在有纹理情况下的摆放方向  0：水平摆放，1：竖直摆放

    # 整理数据，矩形从大到小排列，结合数量，得到一个总的需要排列的矩形列表 all_shapes
    # 结合纹理和横竖排列，返回矩形列表 shape_list
    all_shapes, shape_list, shape_num = tidy_shape(SHAPE, SHAPE_NUM, is_texture, is_vertical)
    # 初始化参数
    empty_place_list = [(0, 0, WIDTH, HEIGHT)]  # 空余地方
    situation_list = list()  # 记录每一块板的排列情况
    is_new = True  # 是否新加一块板
    num_platform = 0
    while len(all_shapes) > 0:
        # 初始化参数
        is_done = False
        if is_new:
            tmp_situation = list()
            empty_place_list = [(0, 0, WIDTH, HEIGHT)]
            is_new = False
            num_platform += 1
            # 在新空间里面放入最大面积的
            for shape in shape_list:
                # 如果已经没有需要安排的图形就跳过
                if shape not in all_shapes:
                    continue
                else:
                    index_shape = all_shapes.index(shape)
                    sub_tmp_situation, sub_empty_place_list = find_one_best(
                        shape[0],
                        shape[1],
                        (0, 0, WIDTH, HEIGHT),
                        all_shapes.count(shape),    # 找剩余的图片数量
                        is_texture,
                        BORDER
                    )
                    empty_place_list.remove((0, 0, WIDTH, HEIGHT))
                    empty_place_list += sub_empty_place_list
                    empty_place_list = tidy_empty_place(empty_place_list)
                    # print(index_shape, len(sub_tmp_situation), shape)
                    for i in range(0, len(sub_tmp_situation)):
                        all_shapes.pop(index_shape)
                    tmp_situation += sub_tmp_situation
                    break

        # 剩余空间里面找最大利用率的图形
        tmp_empty_place = copy.deepcopy(empty_place_list)
        for place in tmp_empty_place:
            # 在特定空间找最优解
            best_rate = 0
            best_situation = None
            best_empty_place = None
            best_index = None
            # best_shape = None
            for shape in shape_list:
                # 如果已经没有需要安排的图形就跳过
                if shape not in all_shapes:
                    continue
                else:
                    # 找最优解，保留最优解
                    index_shape = all_shapes.index(shape)
                    sub_tmp_situation, sub_empty_place_list = find_one_best(
                        shape[0],
                        shape[1],
                        place,
                        all_shapes.count(shape),    # 找剩余的图片数量
                        is_texture,
                        BORDER
                    )
                    if len(sub_tmp_situation) > 0:
                        # 如果有解
                        is_done = True
                        tmp_rate = use_rate(sub_tmp_situation, place[2] - place[0], place[3] - place[1])
                        if tmp_rate > best_rate:
                            best_situation = sub_tmp_situation
                            best_rate = tmp_rate
                            best_empty_place = sub_empty_place_list
                            best_index = index_shape
                            # best_shape = shape

            if is_done:
                empty_place_list.remove(place)
                empty_place_list += best_empty_place
                empty_place_list = tidy_empty_place(empty_place_list)
                break
        if is_done:
            # 把所有已经找到安排的图形剔除
            # print(best_index, len(best_situation), best_shape)
            for i in range(0, len(best_situation)):
                all_shapes.pop(best_index)
            tmp_situation += best_situation
        else:
            is_new = True
            situation_list.append(tmp_situation)


    # 计算使用率
    rate_list = list()
    total_rate = 0
    for s in situation_list:
        r = use_rate(s, WIDTH, HEIGHT)
        total_rate += r
        rate_list.append(r)
    avg_rate = int((total_rate / len(situation_list) * 100)) / 100.0
    title = 'Average rate : %s' % str(avg_rate)

    # 把排版结果显示并且保存
    draw_one_pic(situation_list, rate_list, title, WIDTH, HEIGHT,
                 path=pathname, shapes=shape_list, shapes_num=shape_num, avg_rate=avg_rate)

    return {'error': False, 'rate': avg_rate}


def get_empty_situation(empty_places, min_shape, border):
    """
    把空白的地方转换成画图的格式，如果空白地方最小图形都放不下，就不要了
    :param empty_places:
    :param min_shape:
    :return:
    """
    situation_list = list()
    for place in empty_places:
        solution = find_model(min_shape[0], min_shape[1], place, border)
        if solution['x'] != 0 or solution['y'] != 0:
            situation_list.append((
                place[0],
                place[1],
                place[2] - place[0],
                place[3] - place[1]
            ))
    return situation_list


