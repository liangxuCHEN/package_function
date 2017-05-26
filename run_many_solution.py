# encoding=utf8
import numpy as np
from package import PackerSolution
from package_tools import find_the_same_position, use_rate, draw_one_pic

"""
    data
    'bin_key': bin_key,
    'solution': best_solution,
    'empty_section': empty_positions,
    'rate': best_rate,
    'algo_id': best_packer,
    'bins_list': bins_list,
"""


if __name__ == '__main__':
    shape_data = '[{"SkuCode":"32050052","Length":548.0,"Width":397.0,"Amount":1},{"SkuCode":"32050519","Length":548.0,"Width":397.0,"Amount":1},{"SkuCode":"32050093","Length":770.0,"Width":362.0,"Amount":2},{"SkuCode":"32050038","Length":372.0,"Width":55.0,"Amount":1},{"SkuCode":"32050093","Length":309.0,"Width":75.0,"Amount":2},{"SkuCode":"32050093","Length":478.0,"Width":75.0,"Amount":1},{"SkuCode":"32050076","Length":780.0,"Width":243.0,"Amount":2},{"SkuCode":"32050038","Length":516.0,"Width":190.0,"Amount":4},{"SkuCode":"32050434","Length":295.0,"Width":142.0,"Amount":8},{"SkuCode":"32050434","Length":428.0,"Width":142.0,"Amount":4},{"SkuCode":"32050076","Length":438.0,"Width":291.0,"Amount":4},{"SkuCode":"32050093","Length":478.0,"Width":58.0,"Amount":1}]'

    bin_data = '[{"SkuCode":"32050052","ItemName":"三聚氰胺板-双面仿古白哑光单保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050519","ItemName":"三聚氰胺板-双面仿古白哑光双保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050093","ItemName":"三聚氰胺板-双面仿古白哑光(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050038","ItemName":"三聚氰胺板-双面仿古白哑光单保(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050076","ItemName":"三聚氰胺板-双面仿古白哑光(5mm)","SkuName":"2440*1220*5mm","HasGrain":"否"},{"SkuCode":"32050434","ItemName":"三聚氰胺板-2#8834双面仿橡胶木哑光(12mm)","SkuName":"2440*1220*12mm","HasGrain":"是"}]'
    num_pic = 1

    # 保存之前的五个结果，求方差
    rate_res = list()
    num_save = 5
    max_var_rate = 0.00001
    while True:
        packer = PackerSolution(shape_data, bin_data, border=5, num_pic=num_pic)
        if packer.is_valid():
            res = packer.find_solution(algo_list=[0, 4, 40, 8, 20, 44])
            # 保存总的平均使用率
            tmp_avg_rate = 0
            for data in res:
                best_solution = data['solution']
                bins_list = data['bins_list']
                tmp_avg_rate += data['rate']

                # 计算使用率
                rate_list = list()
                for s_id in range(0, len(best_solution)):
                    r = use_rate(best_solution[s_id], bins_list[s_id][0], bins_list[s_id][1])
                    rate_list.append(r)

                with open(u'四斗柜TESTDI2E00001.txt', 'a+') as f:
                    f.write('%d,%s,%d,%s\n' % (num_pic, data['bin_key'], len(best_solution), str(data['rate'])))

            if num_pic > num_save:
                rate_res.pop(0)
                rate_res.append(tmp_avg_rate / num_save)
                np_arr = np.array(rate_res)
                var_rate = np_arr.var()
                print ('%d: var=%f' % (num_pic, var_rate))
                if var_rate < max_var_rate:
                    break
            else:
                rate_res.append(tmp_avg_rate / num_save)

        else:
            print packer.error_info()

        num_pic += 1


