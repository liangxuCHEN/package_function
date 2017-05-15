# encoding=utf8
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
    input_data = "1142 60 7;1160 539 7;1498 398 7;168 168 7;1872 176 7;1872 214 7;1888 116 7;1888 562 7;1898 538 7;1900 298 7;1900 600 7;1910 128 7;1910 396 7;1910 398 7;218 198 7;295 110 7;319 136 7;326 58 7;340 110 7;340 55 7;386 362 7;396 110 7;396 456 7;406 291 7;446 75 7;484 190 7;508 161 7;516 397 7;542 90 7;607 52 7;632 70 7;710 110 7;720 336 7;759 534 7;760 536 7;798 190 7;812 588 7;830 597 7;842 298 7;842 398 7;850 52 7"
    BORDER = 5  # 产品间的间隔, 算在损耗中
    is_texture = 0  # 是否有纹理，有纹理不能旋转 0：没有， 1：有
    is_vertical = 0  # 当在有纹理情况下的摆放方向  0：水平摆放，1：竖直摆放

    res = get_shape_data(input_data, WIDTH)
    SHAPE = res['shape_list']
    SHAPE_NUM = res['shape_num']
    all_shapes, shape_list, num_shapes = tidy_shape(SHAPE, SHAPE_NUM, is_texture, is_vertical)

    packer_blsf_lside = packer.PackerBFF(pack_algo=guillotine.GuillotineBlsfMaxas,
                                         sort_algo=packer.SORT_LSIDE, rotation=True)
    packer_bls_sside = packer.PackerBBF(pack_algo=guillotine.GuillotineBlsfLas,
                                        sort_algo=packer.SORT_SSIDE, rotation=True)
    packer_baf_lside = packer.PackerBBF(pack_algo=guillotine.GuillotineBafMinas,
                                        sort_algo=packer.SORT_LSIDE, rotation=True)

    packer_bss_lside = packer.PackerBBF(pack_algo=guillotine.GuillotineBssfSas,
                                        sort_algo=packer.SORT_LSIDE, rotation=True)
    packer_bas_sside = packer.PackerBBF(pack_algo=guillotine.GuillotineBafSlas,
                                        sort_algo=packer.SORT_SSIDE, rotation=True)

    # newPacker(mode=PackingMode.Offline,
    #           bin_algo=PackingBin.BBF,
    #           pack_algo=MaxRectsBssf,
    #           sort_algo=SORT_AREA,
    #           rotation=True):

    # Add the rectangles to packing queue
    for r in all_shapes:
        packer_blsf_lside.add_rect(*r)
        packer_bls_sside.add_rect(*r)
        packer_baf_lside.add_rect(*r)
        packer_bss_lside.add_rect(*r)
        packer_bas_sside.add_rect(*r)

    # Add the bins where the rectangles will be placed
    NUM = 50
    packer_blsf_lside.add_bin(WIDTH, HEIGHT, NUM)
    packer_bls_sside.add_bin(WIDTH, HEIGHT, NUM)
    packer_baf_lside.add_bin(WIDTH, HEIGHT, NUM)
    packer_bss_lside.add_bin(WIDTH, HEIGHT, NUM)
    packer_bas_sside.add_bin(WIDTH, HEIGHT, NUM)

    # Start packing
    best_rate = 0
    min_bin_num = NUM
    solution = None
    packer_blsf_lside.pack()
    avg_rate, bin_num, tmp_solution = output_res(packer_blsf_lside.rect_list())
    if min_bin_num > bin_num or (avg_rate > best_rate and bin_num == min_bin_num):
        solution = tmp_solution
        print '0', len(solution)
        min_bin_num = bin_num
        best_rate = avg_rate

    packer_bls_sside.pack()
    avg_rate, bin_num, tmp_solution = output_res(packer_bls_sside.rect_list())
    if min_bin_num > bin_num or (avg_rate > best_rate and bin_num == min_bin_num):
        solution = tmp_solution
        print '1', len(solution)
        min_bin_num = bin_num
        best_rate = avg_rate

    packer_baf_lside.pack()
    avg_rate, bin_num, tmp_solution = output_res(packer_baf_lside.rect_list())
    if min_bin_num > bin_num or (avg_rate > best_rate and bin_num == min_bin_num):
        solution = tmp_solution
        print '2', len(solution)
        min_bin_num = bin_num
        best_rate = avg_rate

    packer_bss_lside.pack()
    avg_rate, bin_num, tmp_solution = output_res(packer_bss_lside.rect_list())
    if min_bin_num > bin_num or (avg_rate > best_rate and bin_num == min_bin_num):
        solution = tmp_solution
        print '3', len(solution)
        min_bin_num = bin_num
        best_rate = avg_rate

    packer_bas_sside.pack()
    avg_rate, bin_num, tmp_solution = output_res(packer_bas_sside.rect_list())
    if min_bin_num > bin_num or (avg_rate > best_rate and bin_num == min_bin_num):
        solution = tmp_solution
        print '4', len(solution)
        min_bin_num = bin_num
        best_rate = avg_rate


    # 计算使用率
    rate_list = list()
    total_rate = 0
    for s in solution:
        r = use_rate(s, WIDTH, HEIGHT)
        total_rate += r
        rate_list.append(r)

    title = 'Average rate : %s' % str(best_rate)
    print best_rate, min_bin_num, len(solution)
    draw_one_pic(solution, rate_list, title, WIDTH, HEIGHT, path='2d_lib_mix_5', border=1,
                 shapes=shape_list, shapes_num=num_shapes, avg_rate=avg_rate, empty_positions=[list()]*len(solution))