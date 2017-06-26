# encoding=utf8
import copy
from package_tools import use_rate, draw_one_pic

"""
计算一个矩形组件的使用率
输入组件尺寸和板材尺寸
返回使用率和排列方式
"""
SIDE_CUT = 10  # 板材的切边宽带


def update_empty_place(solution, shape_x, shape_y, border):
    res = list()
    # 添加放置位置
    if solution['model'] == 'w':
        # 第一种情况
        total_h = solution['place'][1] + shape_y
        while solution['place'][3] >= total_h:
            for i in range(0, solution['x']):
                res.append(
                    (solution['place'][0] + i * shape_x + i * border,
                     total_h - shape_y,
                     shape_x, shape_y)
                )
            total_h += shape_y + border

        begin_x = solution['place'][0] + solution['x'] * shape_x + solution['x'] * border
        # 第二种情况
        total_h = solution['place'][1] + shape_x
        while solution['place'][3] >= total_h:
            for i in range(0, solution['y']):
                res.append(
                    (begin_x + i * shape_y + i * border,
                     total_h - shape_x,
                     shape_y, shape_x)
                )
            total_h += shape_x + border
    else:
        # 第一种情况
        total_w = solution['place'][0] + shape_y
        while solution['place'][2] >= total_w:
            for i in range(0, solution['x']):
                res.append(
                    (total_w - shape_y,
                     solution['place'][1] + i * shape_x + i * border,
                     shape_y, shape_x)
                )
            total_w += shape_y + border
        begin_y = solution['place'][1] + solution['x'] * shape_x + solution['x'] * border
        # 第二种情况
        total_w = solution['place'][0] + shape_x
        while solution['place'][2] >= total_w:
            for i in range(0, solution['y']):
                res.append(
                    (total_w - shape_x,
                     begin_y + i * shape_y + i * border,
                     shape_x, shape_y)
                )
            total_w += shape_x + border
    return res


def cal_rate_num(shape_x, shape_y, length, other, border):
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
    # 拆分矩形,找适合的矩形, 坐标表示矩形:(0,0,30,40) = begin(0,0), end(30,40)
    # 如果长宽一样，就忽略，若不等，判断怎么放，横竖组合，然后看剩余多少
    width = place[2] - place[0]
    height = place[3] - place[1]
    solution_1 = cal_rate_num(shape_x, shape_y, width, height, border)
    solution_1['model'] = 'w'
    solution_1['place'] = place
    solution_2 = cal_rate_num(shape_x, shape_y, height, width, border)
    solution_2['model'] = 'h'
    solution_2['place'] = place
    if solution_1['empty'] > solution_2['empty']:
        return solution_2
    else:
        return solution_1


def find_empty_place(shape_x, solution, border):
    # 找出分割的，更新empty_place
    empty_place = list()
    if solution['model'] == 'w':
        empty_place.append((
            solution['place'][0],
            solution['place'][1],
            solution['place'][0] + solution['x'] * shape_x + border * (solution['x']-1),
            solution['place'][3]
        ))
        empty_place.append((
            solution['place'][0] + solution['x'] * shape_x + border * solution['x'],
            solution['place'][1],
            solution['place'][2],
            solution['place'][3]
        ))
    else:
        empty_place.append((
            solution['place'][0],
            solution['place'][1],
            solution['place'][2],
            solution['place'][1] + solution['x'] * shape_x + border * (solution['x'] - 1)
        ))
        empty_place.append((
            solution['place'][0],
            solution['place'][1] + solution['x'] * shape_x + border * solution['x'],
            solution['place'][2],
            solution['place'][3]
        ))
    return empty_place


def use_rate_data_is_valid(data):
    try:
        shape_x = int(data['shape_x'])
        shape_y = int(data['shape_y'])
        WIDTH = int(data['width'])
        HEIGHT = int(data['height'])
        BORDER = float(data['border'])
    except ValueError:
        return {'error': True, 'info': u'输入类型错误，输入值必须是数值类型'}

    if shape_x <= 0 or shape_y <= 0 or WIDTH <= 0 or HEIGHT <= 0:
        return {'error': True, 'info': u'输入尺寸数值错误，尺寸输入值必须大于零'}
    if shape_x > WIDTH or shape_y > WIDTH:
        return {'error': True, 'info': u'输入尺寸数值错误，组件尺寸必须小于板材'}
    if BORDER < 0:
        return {'error': True, 'info': u'输入尺寸数值错误，组件间隙不能小于零'}
    return {'error': False}


def main_process(data, pathname, side_cut=SIDE_CUT):
    shape_x = int(data['shape_x'])
    shape_y = int(data['shape_y'])
    WIDTH = int(data['width'])
    HEIGHT = int(data['height'])
    # 防止输入长宽位置错，自动调整
    if WIDTH < HEIGHT:
        WIDTH, HEIGHT = HEIGHT, WIDTH
    BORDER = float(data['border'])
    is_texture = int(data['is_texture'])
    is_vertical = int(data['is_vertical'])
    # 整理图形
    if is_texture == 1:
        if is_vertical == 1:
            shape_x, shape_y = shape_y, shape_x
        # 有纹理的，单方向
        solution = {
            'y': 0,
            'x': int(WIDTH + BORDER) / int((shape_x + BORDER)),
            'empty': WIDTH * HEIGHT,  # 最小空白地方，初始值为整个
            'model': 'w',
            'place': (0, 0, WIDTH, HEIGHT)
        }
        situation = update_empty_place(solution, shape_x, shape_y, BORDER)
    else:
        # 没有纹理的
        solution = find_model(shape_x, shape_y, (0, 0, WIDTH, HEIGHT), BORDER)

        # 更新目前的布局情况
        split_place = find_empty_place(shape_x, solution, BORDER)
        situation = update_empty_place(solution, shape_x, shape_y, BORDER)
        while True:
            # 再次判断，找更好的情况
            tmp_situation = list()
            tmp_split_place = list()
            for e_place in split_place:
                solution = find_model(shape_x, shape_y, e_place, BORDER)
                tmp_split_place += find_empty_place(shape_x, solution, BORDER)
                tmp_situation += update_empty_place(solution, shape_x, shape_y, BORDER)

            # 有更好的情况，就更新
            if len(tmp_situation) > len(situation):
                situation = copy.deepcopy(tmp_situation)
                split_place = copy.deepcopy(tmp_split_place)
            else:
                break

    rate = use_rate(situation, WIDTH, HEIGHT, side_cut)
    rate = int(rate*100)/100.0
    if pathname is not None:
        try:
            draw_one_pic([situation], [rate], width=WIDTH, height=HEIGHT, path=pathname, border=1)
        except Exception as e:
            return {'error': True, 'info': u'作图过程中出错，没有图片', 'rate':rate}

    return {'rate': rate, 'error': False, 'amount': len(situation)}

