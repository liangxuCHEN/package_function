# encoding=utf8
import copy
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches


def use_rate(use_place, width, height):
    total_use = 0
    for b_x, b_y, w, h in use_place:
        total_use += w * h
    return int(float(total_use)/(width*height+(width+height)*10 - 100) * 10000)/10000.0


def draw_many_pics(positions, width, height, path, border=0):
    i_p = 0
    for position in positions:
        fig1 = Figure(figsize=(12, 6))
        FigureCanvas(fig1)
        ax1 = fig1.add_subplot(111)
        output_obj = list()
        for v in position:
            output_obj.append(patches.Rectangle((v[0], v[1]), v[2], v[3], edgecolor='m', facecolor='blue', lw=border))

        for p in output_obj:
            ax1.add_patch(p)
        ax1.set_xlim(0, width)
        ax1.set_ylim(0, height)
        fig1.savefig('%s_pic%d.png' % (path, i_p), dpi=200)
        i_p += 1


def can_merge_place(place_v1, place_v2):
    """
    判断两个空间是否能合并
    :param place_v1:
    :param place_v2:
    :return:
    可以合并，返回True 和 合并的新空间
    不可以，返回False 和 None
    """
    if place_v1[0] == place_v2[0] and place_v1[2] == place_v2[2] and (
                    place_v1[1] == place_v2[3] or place_v1[3] == place_v2[1]):
        if place_v1[3] > place_v2[3]:
            return True, (place_v2[0], place_v2[1], place_v2[2], place_v1[3])
        else:
            return True, (place_v2[0], place_v1[1], place_v2[2], place_v2[3])
    if place_v1[1] == place_v2[1] and place_v1[3] == place_v2[3] and (
                    place_v1[0] == place_v2[2] or place_v1[2] == place_v2[0]):
        if place_v1[2] > place_v2[2]:
            return True, (place_v2[0], place_v2[1], place_v1[2], place_v2[3])
        else:
            return True, (place_v1[0], place_v2[1], place_v2[2], place_v2[3])
    return False, None


def compute_width_height(shapes, bin_width, bin_height):
    """
    所有图形的边长，由大到小
    :param shapes:
    :param bin_width:
    :param bin_height:
    :return:
    """
    width_list = set()
    height_list = set()
    for shape in shapes:
        if shape[0] <= bin_height:
            width_list.add(shape[0])
            height_list.add(shape[0])
        elif shape[0] <= bin_width:
            width_list.add(shape[0])

        if shape[1] <= bin_height:
            width_list.add(shape[1])
            height_list.add(shape[1])
        elif shape[1] <= bin_width:
            width_list.add(shape[1])

    width_list = order_list(list(width_list))
    height_list = order_list(list(height_list))
    # 排序
    return width_list, height_list


def order_list(input_data):
    for i in range(len(input_data), 1, -1):
        for j in range(0, i-1):
            if input_data[j] < input_data[j + 1]:
                input_data[j], input_data[j + 1] = input_data[j + 1], input_data[j]
    return input_data


def tidy_shape(shapes, shapes_num, texture, vertical):
    """
    默认是竖直放置, shape_x 是 宽 ， shape_y 是 长, 由大到小排序
    当有纹理并且是竖直摆放的时候，要选择矩形
    :param shapes: 记录各矩形的长宽
    :param shapes_num:  记录矩形的数量
    :param texture:  是否有纹理，0：没有，1：有
    :param vertical: 摆放方式，当有纹理的时候有用，0:水平摆放，1:竖直摆放
    :return:
    """
    tmp_list = list()
    if texture == 1 and vertical == 0:
        # 这里是水平放置
        for shape in shapes:
            shape_x = shape[0]
            shape_y = shape[1]
            if shape_x < shape_y:
                shape_x, shape_y = shape_y, shape_x
            tmp_list.append((shape_x, shape_y))
    else:
        for shape in shapes:
            shape_x = shape[0]
            shape_y = shape[1]
            if shape_x > shape_y:
                shape_x, shape_y = shape_y, shape_x
            tmp_list.append((shape_x, shape_y))

    # 结合数量，合并成一个新的队列
    index_shape = 0
    new_list = list()
    for shape in tmp_list:
        for num in range(0, shapes_num[index_shape]):
            new_list.append(shape)
        index_shape += 1
    return new_list, tmp_list, shapes_num


def write_desc_doc(shapes, shapes_num, path, width, height, positions, num_list, rates, avg_rate, empty_positions):
    """
    描述这个方案的整体结果的文档
    """
    with open('%s_desc.txt' % path, 'w') as f:
        f.write('# : %d x %d  Qty: %d  Rate: %s \n' % (width, height, len(positions), str(avg_rate)))
        for i_shape in range(0, len(shapes)):
            f.write('%d : %d x %d  Qty: %d \n' % (i_shape, shapes[i_shape][0], shapes[i_shape][1], shapes_num[i_shape]))
        f.write('------------- \n')
        f.write('Detail: \n')
        f.write('------------- \n')
        f.write('#  Rate  Qty  \n')
        i_pic = 0
        for i_p in range(0, len(positions)):
            if num_list[i_p] != 0:
                f.write('B%d  %s  %d \n' % (i_pic, str(rates[i_p]), num_list[i_p]))
                i_pic += 1
                # TODO: 组件在每个板材的位置和数量
        f.write('------------- \n')
        f.write('Empty place: \n')
        f.write('------------- \n')
        i_place = 0
        for em_places in empty_positions:
            for em_place in em_places:
                f.write('E%d %d x %d \n' % (i_place, em_place[2], em_place[3]))
                i_place += 1


def draw_one_pic(positions, rates, width=None, height=None, path=None, border=0, num_list=None,
                 shapes=None, empty_positions=None, title=None, bins_list=None):
    # 多个图像需要处理

    if shapes is not None:
        if num_list is None:
            # 返回唯一的排版列表，以及数量
            num_list = find_the_same_position(positions)

    else:
        # 单个图表
        num_list = [1]

    i_p = 0     # 记录板材索引
    i_pic = 1   # 记录图片的索引
    num = len(del_same_data(num_list, num_list))
    fig_height = num * 4
    fig1 = Figure(figsize=(8, fig_height))
    # 使用中文
    # path_ttc = os.path.join(settings.BASE_DIR, 'static')
    # path_ttc = os.path.join(path_ttc, 'simsun.ttc')
    font_set = FontProperties(fname='simsun.ttc', size=12)

    if title is not None:
        fig1.suptitle(title, fontweight='bold', fontproperties=font_set)
    FigureCanvas(fig1)

    for position in positions:
        if num_list[i_p] != 0:
            ax1 = fig1.add_subplot(num, 1, i_pic, aspect='equal')
            i_pic += 1
            ax1.set_title(u'利用率: %s, 数量: %d' % (str(rates[i_p]), num_list[i_p]), fontproperties=font_set)
            output_obj = list()
            for v in position:
                output_obj.append(
                    patches.Rectangle((v[0], v[1]), v[2], v[3], edgecolor='black', lw=border, facecolor='none'))

            if empty_positions is not None:
                for em_v in empty_positions[i_p]:
                    output_obj.append(
                        patches.Rectangle(
                            (em_v[0], em_v[1]), em_v[2], em_v[3], edgecolor='black',
                            lw=border, hatch='/', facecolor='none'))

            for p in output_obj:
                ax1.add_patch(p)
                # 计算显示位置
                if shapes is not None:
                    rx, ry = p.get_xy()
                    cx = rx + p.get_width() / 2.0
                    cy = ry + p.get_height() / 2.0
                    # 找到对应的序号
                    p_id = -1
                    if (p.get_width(), p.get_height()) in shapes:
                        p_id = shapes.index((p.get_width(), p.get_height()))
                    if (p.get_height(), p.get_width()) in shapes:
                        p_id = shapes.index((p.get_height(), p.get_width()))

                    ax1.annotate(p_id, (cx, cy), color='black', weight='bold',
                                 fontsize=6, ha='center', va='center')
            # 坐标长度
            if width is not None and height is not None:
                ax1.set_xlim(0, width)
                ax1.set_ylim(0, height)
            elif bins_list is not None:
                ax1.set_xlim(0, bins_list[i_p][0])
                ax1.set_ylim(0, bins_list[i_p][1])
            else:
                ax1.set_xlim(0, 2430)
                ax1.set_ylim(0, 1210)

        i_p += 1

    if path is not None:
        fig1.savefig('%s.png' % path)
    else:
        fig1.show()


def find_the_same_position(positions):
    # 初始化，默认每个都不一样，数量都是1
    num_list = [1] * len(positions)
    for i in range(len(positions)-1, 0, -1):
        for j in range(0, i):
            if positions[i] == positions[j] and num_list[j] != 0:
                num_list[i] += 1
                num_list[j] = 0
    return num_list


def find_small_shape(shape_list):
    if len(shape_list) == 1:
        return shape_list[0]

    min_size = shape_list[0][0] * shape_list[0][1]
    min_shape = shape_list[0]

    for j in range(1, len(shape_list)):
        # 找最小面积
        if shape_list[j][0] * shape_list[j][1] < min_size:
            min_size = shape_list[j][0] * shape_list[j][1]
            min_shape = shape_list[j]

    return min_shape


def draw_the_pic(position, width, height, border=1, filename=None):
    fig1 = Figure(figsize=(12, 6))
    FigureCanvas(fig1)
    ax1 = fig1.add_subplot(111)
    output_obj = list()
    color_list = ['red', 'blue', 'yellow', 'black']
    index_v = 0
    for v in position:
        output_obj.append(patches.Rectangle((v.x, v.y), v.width, v.height, edgecolor='m', label='Label',
                                            facecolor=color_list[index_v % len(color_list)], lw=border))
        index_v += 1

    for p in output_obj:
        ax1.add_patch(p)

    ax1.set_xlim(0, width)
    ax1.set_ylim(0, height)
    fig1.savefig('%s.png' % filename, dpi=400)


def is_valid_empty_section(empty_sections):
    # TODO: 参数调整预料判断
    min_size = 200000    # 面积 0.2 m^2
    min_height = 58      # 最小边长 58 mm
    total_ares = 0
    res_empty_section = list()
    for sections in empty_sections:
        section_list = list()
        for section in sections:
            if section[2] * section[3] > min_size and min(section[2], section[3]) > min_height:
                section_list.append(section)
                total_ares += section[2] * section[3]

        res_empty_section.append(section_list)

    return res_empty_section, total_ares


def del_same_data(same_bin_list, data_list):
    if len(same_bin_list) != len(data_list):
        return data_list
    res = list()
    for id_data in range(0, len(data_list)):
        if int(same_bin_list[id_data]) != 0:
            res.append(data_list[id_data])
    return res


def get_shape_data(shape_data, bin_data, num_pic=1):
    """
    shape_data 输入是一个字符串如：板A 400 500 30;板A 130 250 10;板B 800 900 5;
    bin_data : A 三聚氰胺板-双面胡桃木哑光(J2496-4)25mm 2430*1210*18 是;B 三聚氰胺板-双面白布纹哑光（18mm） 2430 1210 0 0;
    没有空格，然后通过处理，返回一个字典

    :param data:
    :return:
    {'板A': {
            'shape_list': [(400,500), (130,250)]  一个矩形的长宽
            'shape_num':  [30,10] 对应矩形的数量
            'name': 三聚氰胺板-双面胡桃木哑光(J2496-4)25mm
            'width': 2430,
            'height': 1210,
            'is_texture': 0     是否有纹理，有纹理不能旋转 0：没有， 1：有
            'is_vertical': 0    当在有纹理情况下的摆放方向  0：水平摆放，1：竖直摆放
        },
    '板B': {
            'shape_list': [(800, 900)]  一个矩形的长宽
            'shape_num': [5] 对应矩形的数量
            'name': 三聚氰胺板-双面白布纹哑光（18mm）
            'width': 2430,
            'height': 1210,
            'is_texture': 1
            'is_vertical': 0
        }
    }


    """
    defaut_width = 2430
    defaut_height = 1210
    data_dict = {}     # 返回结果
    bin_list = list()  # 板木种类
    # 板材信息
    bins = bin_data.split(';')
    for abin in bins:
        try:
            # 输入参数有可能6个或5个或4个或3个
            res = abin.split(' ')
            if len(res) == 6:
                bin_type = res[0]
                name = res[1]
                b_w = res[2]
                b_h = res[3]
                is_t = res[4]
                is_v = res[5]
            elif len(res) == 5:
                bin_type = res[0]
                name = res[1]
                b_w = res[2]
                b_h = res[3]
                is_t = res[4]
                is_v = 0
            # 需要处理板材长宽
            elif len(res) == 4 or len(res) == 3:
                bin_type = res[0]

                try:
                    len_res = res[2].split('*')
                    b_w = int(len_res[0]) - 10
                    b_h = int(len_res[1]) - 10
                except:
                    b_w = defaut_width
                    b_h = defaut_height

                try:
                    if res[3] == u'是':
                        is_t = 1
                    else:
                        is_t = 0
                except:
                    is_t = 0

                is_v = 0
                if is_t == 1:
                    name = res[1] + ' ' + res[2] + u' 有纹理'
                else:
                    name = res[1] + ' ' + res[2] + u' 无纹理'
            else:
                return {
                    'error': True,
                    'info': u'板木数据输入有误，缺少参数，至少5个'
                }

            b_w = int(b_w)
            b_h = int(b_h)
            is_t = int(is_t)
            is_v = int(is_v)
            if b_w < b_h:
                b_w, b_h = b_h, b_w

            if bin_type in bin_list:
                return {
                    'error': True,
                    'info': u'板木数据输入有误，有重复的版木数据'
                }

            data_dict[bin_type] = {
                'shape_list': list(),
                'shape_num': list()
            }
            data_dict[bin_type]['name'] = name
            data_dict[bin_type]['width'] = b_w
            data_dict[bin_type]['height'] = b_h
            data_dict[bin_type]['is_texture'] = is_t
            data_dict[bin_type]['is_vertical'] = is_v
            bin_list.append(bin_type)

        except:
            return {
                'error': True,
                'info': u'板木数据输入的格式不对, 一组数据之间用空格, 数据之间用分号<;>, 最后结尾不要放分号<;>, 而且要用英文标点'
            }
    # 组件尺寸信息
    shapes = shape_data.split(';')
    for shape in shapes:
        try:
            bin_type, x, y, num = shape.split(' ')
            try:
                x = int(x)
                y = int(y)
            except:
                x = float(x)
                y = float(y)
            num = int(num) * num_pic
            if bin_type in bin_list:
                data_dict[bin_type]['shape_list'].append((x, y))
                data_dict[bin_type]['shape_num'].append(num)
            else:
                return {
                    'error': True,
                    'info': u'矩形数据输入有误，没有对应的板木类别'
                }
        except:
            return {
                'error': True,
                'info': u'矩形数据输入的格式不对, 一组数据之间用空格, 数据之间用分号<;>, 最后结尾不要放分号<;>, 而且要用英文标点'
            }
        if x > data_dict[bin_type]['width'] or y > data_dict[bin_type]['width']:
            return {'error': True, 'info': u'输入尺寸数值错误，组件尺寸必须小于板材'}
        if x <= 0 or y <= 0:
            return {'error': True, 'info': u'输入尺寸数值错误，尺寸输入值必须大于零'}
        if num <= 0:
            return {'error': True, 'info': u'输入矩形数量错误，输入值必须大于零'}

    return {'data': data_dict, 'error': False}

