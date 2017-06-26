# encoding=utf8
from my_rectpack_lib.package import PackerSolution
from package_tools import tidy_shape, draw_one_pic, use_rate, is_valid_empty_section
from package_tools import find_the_same_position, get_shape_data




if __name__ == '__main__':

    # WIDTH = 2430
    # HEIGHT = 1210
    # SHAPE = [(367, 43), (959, 575), (313, 276), (80, 69)]
    # SHAPE_NUM = [48, 7, 9, 50]
    shape_data = "32050093 582.0 58.1 22;32050038 732.1 58.8 20"
    bin_data = u"32050093 三聚氰胺板-双面仿古白哑光(18mm) 2440*1220*18mm 否;32050038 三聚氰胺板-双面仿古白哑光单保(18mm) 2440*1220*18mm 否"
    BORDER = 5  # 产品间的间隔, 算在损耗中
    # is_texture = 0  # 是否有纹理，有纹理不能旋转 0：没有， 1：有
    # is_vertical = 0  # 当在有纹理情况下的摆放方向  0：水平摆放，1：竖直摆放
    NUM_PIC = 3   # 生产套数， input_data 里面是一套产品的数量，如果是10套，这是就填10
    packer = PackerSolution(shape_data, bin_data, border=5, num_pic=NUM_PIC)


    # 算法参数
    algo_list = None   # 全选, 或 [1,2,3] 表示 选择算法的id

    if packer.is_valid():
        res = packer.find_solution()
        for data in res:
            best_solution = data['solution']
            bins_list = data['bins_list']

        # 把排版结果显示并且保存
        # 返回唯一的排版列表，以及数量
        same_bin_list = find_the_same_position(best_solution)

        draw_one_pic(best_solution, rate_list, values['width'], values['height'],
                     path='package_float' + bin_type, border=1, num_list=same_bin_list, title=title,
                     shapes=shape_list, empty_positions=empty_positions)
