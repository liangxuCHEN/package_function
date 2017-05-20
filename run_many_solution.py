# encoding=utf8
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
    'shape_list': shape_list
"""


if __name__ == '__main__':
    shape_data = '[{"SkuCode":"32050038","Length":1294.0,"Width":398.0,"Amount":9},{"SkuCode":"32050093","Length":1444.0,"Width":296.0,"Amount":9},{"SkuCode":"32010004","Length":1056.0,"Width":279.0,"Amount":9},{"SkuCode":"32010004","Length":1200.0,"Width":330.0,"Amount":9},{"SkuCode":"32050051","Length":2010.0,"Width":128.0,"Amount":18},{"SkuCode":"32050052","Length":1444.0,"Width":456.0,"Amount":9},{"SkuCode":"32050052","Length":1444.0,"Width":163.0,"Amount":9}]'
    bin_data = '[{"SkuCode":"32050038","ItemName":"三聚氰胺板-双面仿古白哑光单保(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050093","ItemName":"三聚氰胺板-双面仿古白哑光(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32010004","ItemName":"中纤板(E1)-B(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050051","ItemName":"三聚氰胺板-双面仿古白哑光(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050052","ItemName":"三聚氰胺板-双面仿古白哑光单保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"}]'
    for num_pic in range(0, 500):
        packer = PackerSolution(shape_data, bin_data, border=5, num_pic=num_pic)
        if packer.is_valid():
            res = packer.find_solution(algo_list=[0, 4, 40, 8, 20, 44])
            for data in res:
                best_solution = data['solution']
                bins_list = data['bins_list']

                # 计算使用率
                rate_list = list()
                for s_id in range(0, len(best_solution)):
                    r = use_rate(best_solution[s_id], bins_list[s_id][0], bins_list[s_id][1])
                    rate_list.append(r)

                with open('bed_105.txt', 'a+') as f:
                    f.write('%d,%s,%d,%s\n' % (num_pic, data['bin_key'], len(best_solution), str(data['rate'])))

        else:
            print packer.error_info()


