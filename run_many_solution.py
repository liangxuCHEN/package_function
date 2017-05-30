# encoding=utf8
import numpy as np
from package import PackerSolution
from package_tools import draw_rates

"""
    data
    'bin_key': bin_key,
    'solution': best_solution,
    'empty_section': empty_positions,
    'rate': best_rate,
    'algo_id': best_packer,
    'bins_list': bins_list,
"""


def main_process(num, packer, filename):

    res = packer.find_solution(algo_list=[0, 4, 40, 8, 20, 44, 24])
    # 平均使用率
    tmp_avg_rate = 0
    for data in res:
        # best_solution = data['solution']
        tmp_avg_rate += data['rate']

        # with open(filename, 'a+') as f:
        #     f.write('%d,%s,%d,%s\n' % (num, data['bin_key'], len(best_solution), str(data['rate'])))

    return tmp_avg_rate / len(res)


if __name__ == '__main__':
    shape_data = '[{"SkuCode":"32050093","Length":596.0,"Width":475.0,"Amount":2},{"SkuCode":"32050038","Length":596.0,"Width":475.0,"Amount":2},{"SkuCode":"32050093","Length":463.0,"Width":320.0,"Amount":2},{"SkuCode":"32050076","Length":581.0,"Width":471.0,"Amount":4},{"SkuCode":"32050051","Length":1188.0,"Width":296.0,"Amount":2},{"SkuCode":"32050093","Length":320.0,"Width":168.0,"Amount":3},{"SkuCode":"32050093","Length":1910.0,"Width":236.0,"Amount":1},{"SkuCode":"32050093","Length":1910.0,"Width":168.0,"Amount":1},{"SkuCode":"32050051","Length":1910.0,"Width":342.0,"Amount":1},{"SkuCode":"32050093","Length":573.0,"Width":342.0,"Amount":3},{"SkuCode":"32050093","Length":1910.0,"Width":360.0,"Amount":1},{"SkuCode":"32050093","Length":1910.0,"Width":296.0,"Amount":1},{"SkuCode":"32050434","Length":1900.0,"Width":600.0,"Amount":2},{"SkuCode":"32050051","Length":1910.0,"Width":396.0,"Amount":1},{"SkuCode":"32050051","Length":1910.0,"Width":128.0,"Amount":1},{"SkuCode":"32050093","Length":1142.0,"Width":60.0,"Amount":2},{"SkuCode":"32050038","Length":1160.0,"Width":539.0,"Amount":2}]'

    bin_data = '[{"SkuCode":"32050093","ItemName":"三聚氰胺板-双面仿古白哑光(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050038","ItemName":"三聚氰胺板-双面仿古白哑光单保(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050076","ItemName":"三聚氰胺板-双面仿古白哑光(5mm)","SkuName":"2440*1220*5mm","HasGrain":"否"},{"SkuCode":"32050051","ItemName":"三聚氰胺板-双面仿古白哑光(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050434","ItemName":"三聚氰胺板-2#8834双面仿橡胶木哑光(12mm)","SkuName":"2440*1220*12mm","HasGrain":"是"}]'

    filename = u'功能床TESTDI5A00001.txt'

    num_pic = 1
    # 保存之前的五个结果，求方差
    rate_res = list()
    num_save = 5
    max_var_rate = 0.00001
    while True:
        packer = PackerSolution(shape_data, bin_data, border=5, num_pic=num_pic)
        if packer.is_valid():
            tmp_avg_rate = main_process(num_pic, packer, filename)
            if num_pic > num_save:
                rate_res.append(tmp_avg_rate)
                np_arr = np.array(rate_res[-1*num_save:])
                var_rate = np_arr.var()
                print ('%d: var=%f' % (num_pic, var_rate))
                if var_rate < max_var_rate:
                    break
            else:
                rate_res.append(tmp_avg_rate)

        else:
            print packer.error_info()

        num_pic += 1

    max_rate = max(rate_res)
    best_pic = rate_res.index(max_rate) + 1
    # with open(filename, 'a+') as f:
    #     f.write('========================Resume=================================\n')
    #     f.write('best piece: %d, max rate: %s\n' % (best_pic, str(max_rate)))

    # 画图
    np_rates = np.array(rate_res)
    x = range(1, len(np_rates)+1)
    draw_rates(np_rates, x, filename)

    # 验证倍数是否最优
    rate_res = list()
    for i in range(1, 4):
        begin_pic = best_pic * i
        for tmp_pic in range(begin_pic, begin_pic+4):
            packer = PackerSolution(shape_data, bin_data, border=5, num_pic=tmp_pic)
            if packer.is_valid():
                tmp_avg_rate = main_process(tmp_pic, packer, filename)
                print ('piece: %d, rate: %s' % (tmp_pic, str(tmp_avg_rate)))
                rate_res.append(tmp_avg_rate)

            else:
                print packer.error_info()

    # 画图
    np_rates = np.array(rate_res)
    x = range(1, len(np_rates) + 1)
    draw_rates(np_rates, x, filename.split('.')[0])


