# encoding=utf8
import json
from my_rectpack_lib.packer import newPacker
import my_rectpack_lib.guillotine as guillotine
import my_rectpack_lib.packer as packer

EMPTY_SECTION_MIN_SIZE = 200000    # 面积 0.2 m^2
EMPTY_SECTION_MIN_HEIGHT = 58      # 最小边长 58 mm


def output_res(all_rects, bins_list):
    rects = list()
    all_positions = list()
    # print bins_list
    is_new_bin = 0
    for rect in all_rects:
        b, x, y, w, h, rid = rect
        if b == is_new_bin:
            rects.append((x, y, w, h))
        else:
            is_new_bin = b
            all_positions.append(rects)
            rects = list()
            rects.append((x, y, w, h))

    all_positions.append(rects)

    # 计算使用率
    total_rate = 0
    for s_id in range(0, len(all_positions)):
        r = use_rate(all_positions[s_id], bins_list[s_id][0], bins_list[s_id][1])
        total_rate += r

    avg_rate = int((total_rate / len(all_positions) * 10000)) / 10000.0
    # print('avg rate : %s, use %d pec bin' % (str(avg_rate), all_rects[-1][0] + 1))
    return avg_rate, all_positions


def use_rate(use_place, width, height):
    total_use = 0
    for b_x, b_y, w, h in use_place:
        total_use += w * h
    return int(float(total_use)/(width*height+(width+height)*10 - 100) * 10000)/10000.0


def get_shape_data_from_json(shape_data, bin_data, bins_num=None, num_pic=1):
    default_width = 2430
    default_height = 1210
    data_dict = {}  # 返回结果
    bin_list = list()  # 板木种类

    # 板木数据
    bins = json.loads(bin_data)
    for bin in bins:
        if bin['SkuCode'] in bin_list:
            return {
                'error': True,
                'info': u'板木数据输入有误，有重复的板木数据'
            }

        try:
            len_res = bin['SkuName'].split('*')
            b_w = int(len_res[0]) - 10
            b_h = int(len_res[1]) - 10
        except:
            b_w = default_width
            b_h = default_height

        try:
            if bin['HasGrain'] == u'是':
                is_t = 1
            else:
                is_t = 0
        except:
            is_t = 0

        bin_type = bin['SkuCode']
        if is_t == 1:
            name = bin['ItemName'] + ' ' + bin['SkuName'] + u' 有纹理'
        else:
            name = bin['ItemName'] + ' ' + bin['SkuName'] + u' 无纹理'

        data_dict[bin_type] = {
            'shape_list': list(),
            'shape_num': list()
        }
        data_dict[bin_type]['name'] = name
        data_dict[bin_type]['width'] = b_w
        data_dict[bin_type]['height'] = b_h
        data_dict[bin_type]['is_texture'] = is_t
        data_dict[bin_type]['is_vertical'] = 0
        bin_list.append(bin_type)

    # 组件数据
    shapes = json.loads(shape_data)
    for shape in shapes:

        try:
            x = int(shape['Length'])
            y = int(shape['Width'])
        except:
            x = float(shape['Length'])
            y = float(shape['Width'])

        if shape['SkuCode'] in bin_list:
            data_dict[shape['SkuCode']]['shape_list'].append((x, y))
            data_dict[shape['SkuCode']]['shape_num'].append(int(shape['Amount']) * num_pic)
        else:
            return {
                'error': True,
                'info': u'矩形数据输入有误，没有对应的板木类别'
            }

        if x > data_dict[bin_type]['width'] or y > data_dict[bin_type]['width']:
            return {'error': True, 'info': u'输入尺寸数值错误，组件尺寸必须小于板材'}
        if x <= 0 or y <= 0:
            return {'error': True, 'info': u'输入尺寸数值错误，尺寸输入值必须大于零'}
        if int(shape['Amount']) <= 0:
            return {'error': True, 'info': u'输入矩形数量错误，输入值必须大于零'}

    # 定制板木（余料复用）数据
    if bins_num is not None:
        for key in data_dict.keys():
            try:
                data_dict[key]['bins_num'] = list()
            except:
                return {'error': True, 'info': u'板木余料数据有误, 没有对应的板木信息'}
        try:
            res = json.loads(bins_num)
            for data in res:
                tmp_size = data['SkuName'].split('*')
                data_dict[data['SkuCode']]['bins_num'].append({
                    'w': int(tmp_size[0]),
                    'h': int(tmp_size[1]),
                    'num': data['Amount']
                })
        except:
            return {'error': True, 'info': u'板木余料数据格式有误'}

    return {'data': data_dict, 'error': False}


def get_shape_data(shape_data, bin_data, bins_num):
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
    data_dict = {}  # 返回结果
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
                    'info': u'板木数据输入有误，有重复的板木数据'
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
            if bin_type in bin_list:
                data_dict[bin_type]['shape_list'].append((x, y))
                data_dict[bin_type]['shape_num'].append(int(num))
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

    # 定制板木（余料复用）数据
    if bins_num is not None:
        for key in data_dict.keys():
            try:
                data_dict[key]['bins_num'] = list()
            except:
                return {'error': True, 'info': u'板木余料数据有误, 没有对应的板木信息'}
        try:
            res = bins_num.split(';')
            for data in res:
                data_key, size_value, num = data.split(' ')
                tmp_size = size_value.split('*')
                data_dict[data_key]['bins_num'].append({
                    'w': int(tmp_size[0]),
                    'h': int(tmp_size[1]),
                    'num': int(num)
                })
        except:
            return {'error': True, 'info': u'板木余料数据格式有误'}

    return {'data': data_dict, 'error': False}


def is_valid_empty_section(empty_sections, min_size, min_height):
    # TODO: 参数调整预料判断
    if min_size is None:
        min_size = EMPTY_SECTION_MIN_SIZE
    if min_height is None:
        min_height = EMPTY_SECTION_MIN_HEIGHT
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


class PackerSolution(object):
    """
    compare all the packer algorithm
    """
    def __init__(self, rects_data, bins_data, border=0,
                 bins_num=None, num_pic=1, empty_section_min_size=None, empty_section_min_len=None):
        """
        :param rect_data: rect_data 输入是一个字符串如：板A 400 500 30;板A 130 250 10;板B 800 900 5;
        :param bin_data:  : A 三聚氰胺板-双面胡桃木哑光(J2496-4)25mm 2430*1210*18 是;B 三聚氰胺板-双面白布纹哑光（18mm） 2430 1210 0 0;
        :param bins_num:  : A 2230*1010*18 3;A 1230*810*18 3
        :param border: 切割间隙
        """
        self._border = border
        self._empty_section_min_size = empty_section_min_size
        self._empty_section_min_len = empty_section_min_len
        try:
            self._data = get_shape_data_from_json(rects_data, bins_data, bins_num, num_pic=num_pic)
        except:
            self._data = get_shape_data(rects_data, bins_data, bins_num)

    def is_valid(self):
        if self._data['error']:
            return False

        return True

    def error_info(self):
        if self._data['error']:
            return self._data['info']

        return None

    def get_bins_key(self):
        if self.is_valid():
            return self._data['data'].keys()

        return None

    def get_bin_data(self, bin_key, key=None):
        if self.is_valid():
            if bin_key in self._data['data'].keys():
                if key and key in self._data['data'][bin_key]:
                    return self._data['data'][bin_key][key]
                else:
                    return self._data['data'][bin_key]
        return None

    def _tidy_shape(self, bin_key):
        """
        默认是竖直放置, shape_x 是 宽 ， shape_y 是 长, 由大到小排序
        当有纹理并且是竖直摆放的时候，要选择矩形
        :param shapes: 记录各矩形的长宽
        :param shapes_num:  记录矩形的数量
        :param texture:  是否有纹理，0：没有，1：有
        :param vertical: 摆放方式，当有纹理的时候有用，0:水平摆放，1:竖直摆放
        :return:
        """
        shapes = self.get_bin_data(bin_key, key='shape_list')
        shapes_num = self.get_bin_data(bin_key, key='shape_num')
        texture = self.get_bin_data(bin_key, key='is_texture')
        vertical = self.get_bin_data(bin_key, key='is_vertical')
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

    def find_best_solution(self, all_shapes, bin_key, packer_id_list=None, bins_num=None):
        """
        遍历各种算法找最佳的方案
        :param all_shapes: 矩形数据
        :param border: 缝隙
        :param bin_width: 板材长
        :param bin_height: 板材宽
        :param is_texture: 是否有纹理
        :param packer_id_list:[0,4,50] :只选用特定算法
        :param bins_num:[{'w':200, 'h':100,'num':10},{'w':1200, 'h':600,'num':10}]
        :return:
        best_solution: 组件的坐标
        best_empty_positions: 余料坐标
        best_rate: 方案的平均利用率
        best_packer: 方案（算法）的ID
        """
        bin_width = self.get_bin_data(bin_key, key='width')
        bin_height = self.get_bin_data(bin_key, key='height')
        # 所有算法组合
        # 当排版的组件非常多，需要提高反应速度可以选择BFF（首次适应）算法
        # bin_algos = [packer.PackingBin.BBF, packer.PackingBin.BFF]
        # 这里选择BBF（最佳适应）算法，可以较好保留大块空余地方。
        bin_algos = [packer.PackingBin.BBF]
        # 这里是选择板材切割算法guillotine,
        # 选择区域标准：BAF:找最佳面积适应, BLSF:最佳长边适应值, BSSF:最佳短边边适应值
        # 分割剩余区域标准：SLAS:剩余短轴分割,LAS:长轴分割,MAXAS:剩余大面积分割:,LLAS:剩余长轴分割,MINAS:剩余小面积分割,
        # TODO：如果是激光切割，可以使用maxrects算法
        pack_algos = [guillotine.GuillotineBafLas, guillotine.GuillotineBafMaxas,
                      guillotine.GuillotineBafMinas, guillotine.GuillotineBafSlas, guillotine.GuillotineBafLlas,
                      guillotine.GuillotineBlsfLas, guillotine.GuillotineBlsfMaxas,
                      guillotine.GuillotineBlsfMinas, guillotine.GuillotineBlsfSlas, guillotine.GuillotineBlsfLlas,
                      guillotine.GuillotineBssfLas, guillotine.GuillotineBssfMaxas,
                      guillotine.GuillotineBssfMinas, guillotine.GuillotineBssfSlas, guillotine.GuillotineBssfLlas]
        # 矩形排序规则,由大到小:
        # SORT_AREA:面积, SORT_LSIDE:长边, SORT_SSIDE:短边, SORT_PERI:周长
        sort_algos = [packer.SORT_AREA, packer.SORT_LSIDE, packer.SORT_SSIDE, packer.SORT_PERI]

        # 按照不同算法规则添加对象
        list_packer = list()
        for bin_alog in bin_algos:
            for pack_alog in pack_algos:
                for sort_algo in sort_algos:
                    list_packer.append(newPacker(bin_algo=bin_alog,
                                                 pack_algo=pack_alog,
                                                 sort_algo=sort_algo,
                                                 rotation=not self.get_bin_data(bin_key, key='is_vertical'),
                                                 border=self._border))

        # 是否选定算法
        if packer_id_list is not None:
            new_packer_list = list()
            for i_packer in packer_id_list:
                new_packer_list.append(list_packer[i_packer])
            list_packer = new_packer_list

        # Add the rectangles to packing queue
        for my_pack in list_packer:
            for r in all_shapes:
                my_pack.add_rect(*r)

        # Add the bins where the rectangles will be placed
        # TODO: 添加出入参数，选择可以使用的板材尺寸和数量
        NUM = 5000
        for my_pack in list_packer:
            if bins_num is not None:
                for abin in bins_num:
                    my_pack.add_bin(abin['w'], abin['h'], abin['num'])

            my_pack.add_bin(bin_width, bin_height, NUM)

        # Start packing
        # 初始化参数
        best_rate = 0.0
        min_bin_num = NUM
        best_solution = None
        best_packer = 0
        index_packer = 0
        best_empty_positions = None
        max_empty_ares = 0

        for my_pack in list_packer:
            my_pack.pack()
            # TODO:avg_rate has errors
            avg_rate, tmp_solution = output_res(my_pack.rect_list(), my_pack.bin_list())
            bin_num = len(tmp_solution)
            # 余料判断
            tmp_empty_position, empty_ares = is_valid_empty_section(
                my_pack.get_sections(), self._empty_section_min_size, self._empty_section_min_len)
            # print(u'算法%d >>> 平均利用率:%s, 使用%d块, 余料总面积:%d' % (
            #    index_packer, str(avg_rate), len(tmp_solution), empty_ares))

            # 找最优解
            if min_bin_num > bin_num or (avg_rate > best_rate and bin_num == min_bin_num) or (
                                bin_num == min_bin_num and avg_rate == best_rate and empty_ares > max_empty_ares):
                best_solution = tmp_solution
                min_bin_num = bin_num
                best_rate = avg_rate
                best_empty_positions = tmp_empty_position
                max_empty_ares = empty_ares
                best_packer = index_packer
            index_packer += 1

        # 板木尺寸信息
        bins_list = list_packer[best_packer].bin_list()

        # 找到真实的id
        if packer_id_list is not None:
            best_packer = packer_id_list[best_packer]

        # print('-------------Result----------------------')
        # print(u'算法%d >>> 平均利用率:%s, 使用%d块, 余料总面积:%d' % (
        #    best_packer, str(best_rate), len(best_solution), max_empty_ares))

        return best_solution, best_empty_positions, best_rate, best_packer, bins_list

    def find_solution(self, algo_list=None):
        if self.is_valid():
            result_list = list()
            for bin_key in self._data['data'].keys():
                all_shapes, shape_list, num_shapes = self._tidy_shape(bin_key)

                # 没有数据
                if len(all_shapes) == 0:
                    continue
                # TODO:bin info
                bins_num = None
                if 'bins_num' in self._data['data'][bin_key]:
                    bins_num = self.get_bin_data(bin_key, key='bins_num')

                best_solution, empty_positions, best_rate, best_packer, bins_list = self.find_best_solution(
                    all_shapes, bin_key, packer_id_list=algo_list, bins_num=bins_num)

                result_list.append({
                    'bin_key': bin_key,
                    'solution': best_solution,
                    'empty_section': empty_positions,
                    'rate': best_rate,
                    'algo_id': best_packer,
                    'bins_list': bins_list,
                    'shape_list': shape_list
                })
            return result_list

        return None

    def _get_bins_num(self, bins_num):
        """
        :param bins_num:  : A 2230*1010*18 3;A 1230*810*18 3
        :return:
        """
        bins_key = self.get_bins_key()
        res_dict = {}
        for key in bins_key:
            res_dict[key] = list()
        try:
            res = bins_num.split(';')
            for data in res:
                data_key, size_value, num = data.split(' ')
                tmp_size = size_value.split('*')
                res_dict[data_key].append({
                    'w': int(tmp_size[0]),
                    'h': int(tmp_size[1]),
                    'num': int(num)
                })
        except:
            return {'error': True, 'info': u'板木余料数据输入有误'}

        return res_dict


