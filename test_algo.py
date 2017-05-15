# encoding=utf8
from  my_rectpack_lib.packer import newPacker
import my_rectpack_lib.guillotine as guillotine
import my_rectpack_lib.packer as packer
from package_function import get_shape_data
from package_tools import tidy_shape, draw_one_pic, use_rate


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


if __name__ == '__main__':

    WIDTH = 2430
    HEIGHT = 1210
    # SHAPE = [(367, 43), (959, 575), (313, 276), (80, 69)]
    # SHAPE_NUM = [48, 7, 9, 50]
    input_data = "1592 190 10;1920 190 10"
    BORDER = 5  # 产品间的间隔, 算在损耗中
    is_texture = 0  # 是否有纹理，有纹理不能旋转 0：没有， 1：有
    is_vertical = 0  # 当在有纹理情况下的摆放方向  0：水平摆放，1：竖直摆放
    NUM_PIC = 1   # 生产套数， input_data 里面是一套产品的数量，如果是10套，这是就填10
    res = get_shape_data(input_data, WIDTH, num_pic=NUM_PIC)
    SHAPE = res['shape_list']
    SHAPE_NUM = res['shape_num']
    print SHAPE
    print SHAPE_NUM
    all_shapes, shape_list, num_shapes = tidy_shape(SHAPE, SHAPE_NUM, is_texture, is_vertical)

    bin_alogs = [packer.PackingBin.BBF, packer.PackingBin.BFF]
    pack_alogs = [guillotine.GuillotineBafLas, guillotine.GuillotineBafMaxas,
                  guillotine.GuillotineBafMinas, guillotine.GuillotineBafSlas, guillotine.GuillotineBafLlas,
                  guillotine.GuillotineBlsfLas, guillotine.GuillotineBlsfMaxas,
                  guillotine.GuillotineBlsfMinas, guillotine.GuillotineBlsfSlas, guillotine.GuillotineBlsfLlas,
                  guillotine.GuillotineBssfLas, guillotine.GuillotineBssfMaxas,
                  guillotine.GuillotineBssfMinas, guillotine.GuillotineBssfSlas, guillotine.GuillotineBssfLlas]
    sort_algos = [packer.SORT_AREA, packer.SORT_LSIDE, packer.SORT_SSIDE, packer.SORT_PERI]

    list_packer = list()
    index_packer = 0
    for bin_alog in bin_alogs:
        for pack_alog in pack_alogs:
            for sort_algo in sort_algos:
                # print(index_packer, str(bin_alog), str(pack_alog), str(sort_algo))
                list_packer.append(newPacker(bin_algo=bin_alog,
                                             pack_algo=pack_alog,
                                             sort_algo=sort_algo,
                                             rotation=not is_texture,
                                             border=BORDER))
                # index_packer += 1

    # Add the rectangles to packing queue
    for my_pack in list_packer:
        for r in all_shapes:
            my_pack.add_rect(*r)

    # Add the bins where the rectangles will be placed
    NUM = 500
    for my_pack in list_packer:
        my_pack.add_bin(WIDTH, HEIGHT, NUM)

    # Start packing
    best_rate = 0
    min_bin_num = NUM
    solution = None
    index_packer = 0
    for my_pack in list_packer:
        my_pack.pack()
        avg_rate, bin_num, tmp_solution = output_res(my_pack.rect_list())
        if min_bin_num > bin_num or (avg_rate > best_rate and bin_num == min_bin_num):
            solution = tmp_solution
            print 'chose:', index_packer, len(solution)
            min_bin_num = bin_num
            best_rate = avg_rate
        elif min_bin_num == bin_num and avg_rate == best_rate:
            print 'index:', index_packer
        index_packer += 1

    # 计算使用率
    rate_list = list()
    total_rate = 0
    for s in solution:
        r = use_rate(s, WIDTH, HEIGHT)
        total_rate += r
        rate_list.append(r)

    title = 'Average rate : %s' % str(best_rate)
    print best_rate, len(solution)
    draw_one_pic(solution, rate_list, title, WIDTH, HEIGHT, path='2d_lib_mix_t11', border=0,
                 shapes=shape_list, shapes_num=num_shapes, avg_rate=avg_rate, empty_positions=[list()]*len(solution))