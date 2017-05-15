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
    input_data = "273 370 5;273 370 5;400 58 4;400 58 4;570 546 3;576 58 2;375 356 2;614 378 2;478 58 2;478 58 2;400 300 2;764 300 2;802 158 2;762 58 2;1130 158 2;1090 58 2;578 396 2;1062 58 2;400 300 2;764 300 2;866 396 2;958 58 2;254 327 2;430 114 1;410 114 1;950 169 1;502 110 1;448 448 1;498 448 1;950 430 1;1200 588 1;1160 76 1;1160 58 1;1160 568 1;548 58 1;2106 588 1;2106 588 1;2030 568 1;386 396 1;1792 398 1;395 378 1;576 378 1;320 120 1;1438 398 1;1058 58 1;804 398 1;269 356 1;624 396 1;624 378 1;624 358 1;362 278 1;590 298 1;1162 298 1;570 298 1;552 298 1;273 370 1;2060 273 1;1470 273 1;590 298 1;570 298 1;552 298 1;273 370 1;2060 273 1;1428 298 1;1470 273 1;273 368 1;273 548 1;430 114 1;410 114 1;502 110 1;468 450 1;448 448 1;546 430 1;546 430 1;498 448 1;950 430 1;800 398 1;370 280 1;600 200 1;800 200 1;530 200 1;1100 350 1;1062 349 1;1002 350 1;926 350 1;362 278 1;472 58 1;510 398 1;1200 600 1;290 596 1;457 290 1;290 556 1;600 200 1;476 190 1;746 396 1;356 184 1;996 398 1;996 396 1;349 184 1;958 196 1;600 200 1;1200 300 1;1798 298 1;275 298 1;1110 352 1;254 327 1;300 300 1;212 300 1;1072 327 1;230 300 1;351 327 1;702 327 1;680 327 1;1672 350 1"
    BORDER = 5  # 产品间的间隔, 算在损耗中
    is_texture = 0  # 是否有纹理，有纹理不能旋转 0：没有， 1：有
    is_vertical = 0  # 当在有纹理情况下的摆放方向  0：水平摆放，1：竖直摆放
    NUM_PIC = 10   # 生产套数， input_data 里面是一套产品的数量，如果是10套，这是就填10
    res = get_shape_data(input_data, WIDTH, num_pic=NUM_PIC)
    SHAPE = res['shape_list']
    SHAPE_NUM = res['shape_num']
    all_shapes, shape_list, num_shapes = tidy_shape(SHAPE, SHAPE_NUM, is_texture, is_vertical)
    print shape_list
    print num_shapes

    # packer_blsf_lside = packer.PackerBFF(pack_algo=guillotine.GuillotineBlsfMaxas,
    #                                      sort_algo=packer.SORT_LSIDE, rotation=True, border=5)
    packer_blsf_lside = newPacker(bin_algo=packer.PackingBin.BFF,
                                  pack_algo=guillotine.GuillotineBlsfMaxas,
                                  sort_algo=packer.SORT_LSIDE,
                                  rotation=not is_texture,
                                  border=BORDER)
    packer_bls_sside = packer.PackerBBF(pack_algo=guillotine.GuillotineBlsfMinas,
                                        sort_algo=packer.SORT_LSIDE, rotation=not is_texture, border=BORDER)
    packer_baf_lside = packer.PackerBBF(pack_algo=guillotine.GuillotineBlsfMaxas,
                                        sort_algo=packer.SORT_LSIDE, rotation=not is_texture, border=BORDER)

    packer_bss_lside = packer.PackerBBF(pack_algo=guillotine.GuillotineBssfSas,
                                        sort_algo=packer.SORT_LSIDE, rotation=not is_texture, border=BORDER)
    packer_bas_sside = packer.PackerBFF(pack_algo=guillotine.GuillotineBssfMinas,
                                        sort_algo=packer.SORT_SSIDE, rotation=not is_texture, border=BORDER)


    # Add the rectangles to packing queue
    for r in all_shapes:
        packer_blsf_lside.add_rect(*r)
        packer_bls_sside.add_rect(*r)
        packer_baf_lside.add_rect(*r)
        packer_bss_lside.add_rect(*r)
        packer_bas_sside.add_rect(*r)

    # Add the bins where the rectangles will be placed
    NUM = 200
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
    print best_rate, len(solution)
    draw_one_pic(solution, rate_list, title, WIDTH, HEIGHT, path='2d_lib_mix_ex_8', border=0,
                 shapes=shape_list, shapes_num=num_shapes, avg_rate=avg_rate, empty_positions=[list()]*len(solution))