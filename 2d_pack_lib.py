# encoding=utf8
from  my_rectpack_lib.packer import newPacker
import my_rectpack_lib.guillotine as guillotine
import my_rectpack_lib.packer as packer
from package_tools import tidy_shape, draw_one_pic, use_rate, find_the_same_position, get_shape_data


def output_res(all_rects):
    rects = list()
    all_positions = list()

    is_new_bin = 0
    for rect in all_rects:
        b, x, y, w, h, rid = rect
        # print b, x, y, w, h, rid
        if b == is_new_bin:
            rects.append((x, y, w, h))
        else:
            is_new_bin = b
            all_positions.append(rects)
            rects = list()
            rects.append((x, y, w, h))

    all_positions.append(rects)

    # 计算使用率
    rate_list = list()
    total_rate = 0
    for s in all_positions:
        r = use_rate(s, WIDTH, HEIGHT)
        total_rate += r
        rate_list.append(r)
    avg_rate = int((total_rate / len(all_positions) * 100)) / 100.0
    print('avg rate : %s, use %d pec bin' % (str(avg_rate), all_rects[-1][0] + 1))
    return avg_rate, all_rects[-1][0], all_positions


def find_best_solution(all_shapes, border, bin_width, bin_height, is_texture, packer_id_list=None):
    """
    遍历各种算法找最佳的方案
    :param all_shapes: 矩形数据
    :param border: 缝隙
    :param bin_width: 板材长
    :param bin_height: 板材宽
    :param is_texture: 是否有纹理
    :param packer_id_list:[0,4,50] :只选用特定算法
    :return:
    best_solution: 组件的坐标
    best_empty_positions: 余料坐标
    best_rate: 方案的平均利用率
    best_packer: 方案（算法）的ID
    """
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
                                             rotation=not is_texture,
                                             border=border))

    # Add the rectangles to packing queue
    for my_pack in list_packer:
        for r in all_shapes:
            my_pack.add_rect(*r)

    # Add the bins where the rectangles will be placed
    # TODO: 添加出入参数，选择可以使用的板材尺寸和数量
    NUM = 5000
    for my_pack in list_packer:
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

    # 是否选定算法
    if packer_id_list is not None:
        new_packer_list = list()
        for i_packer in packer_id_list:
            new_packer_list.append(list_packer[i_packer])
        list_packer = new_packer_list

    for my_pack in list_packer:
        my_pack.pack()
        avg_rate, tmp_solution = output_res(my_pack.rect_list(), bin_width, bin_height)
        bin_num = len(tmp_solution)
        # 余料判断
        tmp_empty_position, empty_ares = is_valid_empty_section(my_pack.get_sections())
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

    # 找到真实的id
    if packer_id_list is not None:
        best_packer = packer_id_list[best_packer]

    return best_solution, best_empty_positions, best_rate, best_packer


if __name__ == '__main__':

    WIDTH = 2430
    HEIGHT = 1210
    # SHAPE = [(367, 43), (959, 575), (313, 276), (80, 69)]
    # SHAPE_NUM = [48, 7, 9, 50]
    input_data = "300 400 20"
    BORDER = 5  # 产品间的间隔, 算在损耗中

    NUM_PIC = 1   # 生产套数， input_data 里面是一套产品的数量，如果是10套，这是就填10
    data = get_shape_data(input_data, WIDTH, num_pic=NUM_PIC)

    # 算法参数
    algo_list = None

    # 每一种板木排版一次
    for bin_type, values in data['data'].items():
        all_shapes, shape_list, num_shapes = tidy_shape(
            values['shape_list'], values['shape_num'], values['is_texture'], values['is_vertical'])
        best_solution, empty_positions, best_rate, best_packer = find_best_solution(
            all_shapes, BORDER, values['width'], values['height'], values['is_texture'], packer_id_list=algo_list)

        # 计算使用率
        rate_list = list()
        for s in best_solution:
            r = use_rate(s, values['width'], values['height'])
            rate_list.append(r)
        title = u'平均利用率: %s' % str(best_rate)
        # 把排版结果显示并且保存
        # 返回唯一的排版列表，以及数量
        same_bin_list = find_the_same_position(best_solution)

        draw_one_pic(best_solution, rate_list, values['width'], values['height'],
                     path='package_test' + bin_type, border=1, num_list=same_bin_list, title=title,
                     shapes=shape_list, empty_positions=empty_positions)
