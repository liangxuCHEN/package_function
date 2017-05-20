# encoding=utf8
from package import PackerSolution
from package_tools import find_the_same_position, use_rate, draw_one_pic


if __name__ == '__main__':
    shape_data = '[{"SkuCode":"32050093","Length":319.0,"Width":136.0,"Amount":10},{"SkuCode":"32050076","Length":406.0,"Width":291.0,"Amount":20},{"SkuCode":"32050434","Length":396.0,"Width":110.0,"Amount":20},{"SkuCode":"32050434","Length":295.0,"Width":110.0,"Amount":40},{"SkuCode":"32050038","Length":484.0,"Width":190.0,"Amount":20},{"SkuCode":"32050076","Length":396.0,"Width":456.0,"Amount":10},{"SkuCode":"32050093","Length":386.0,"Width":362.0,"Amount":20},{"SkuCode":"32050093","Length":446.0,"Width":75.0,"Amount":10},{"SkuCode":"32050519","Length":516.0,"Width":397.0,"Amount":10},{"SkuCode":"32050052","Length":516.0,"Width":397.0,"Amount":10},{"SkuCode":"32050038","Length":340.0,"Width":55.0,"Amount":10},{"SkuCode":"32050038","Length":1294.0,"Width":398.0,"Amount":9},{"SkuCode":"32050093","Length":1444.0,"Width":296.0,"Amount":9},{"SkuCode":"32010004","Length":1056.0,"Width":279.0,"Amount":9},{"SkuCode":"32010004","Length":1200.0,"Width":330.0,"Amount":9},{"SkuCode":"32050051","Length":2010.0,"Width":128.0,"Amount":18},{"SkuCode":"32050052","Length":1444.0,"Width":456.0,"Amount":9},{"SkuCode":"32050052","Length":1444.0,"Width":163.0,"Amount":9}]'
    bin_data = u'[{"SkuCode":"32050093","ItemName":"三聚氰胺板-双面仿古白哑光(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050076","ItemName":"三聚氰胺板-双面仿古白哑光(5mm)","SkuName":"2440*1220*5mm","HasGrain":"否"},{"SkuCode":"32050434","ItemName":"三聚氰胺板-2#8834双面仿橡胶木哑光(12mm)","SkuName":"2440*1220*12mm","HasGrain":"是"},{"SkuCode":"32050038","ItemName":"三聚氰胺板-双面仿古白哑光单保(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050519","ItemName":"三聚氰胺板-双面仿古白哑光双保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050052","ItemName":"三聚氰胺板-双面仿古白哑光单保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32010004","ItemName":"中纤板(E1)-B(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050051","ItemName":"三聚氰胺板-双面仿古白哑光(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"}]'
    packer = PackerSolution(shape_data, bin_data, border=5, num_pic=2,
                            empty_section_min_size=100000, empty_section_min_len=90)
    if packer.is_valid():
        res = packer.find_solution(algo_list=[0, 4, 40, 8, 20])
        for data in res:
            best_solution = data['solution']
            bins_list = data['bins_list']

            # 计算使用率
            rate_list = list()
            for s_id in range(0, len(best_solution)):
                r = use_rate(best_solution[s_id], bins_list[s_id][0], bins_list[s_id][1])
                rate_list.append(r)

            title = u'平均利用率: %s' % str(data['rate'])
            # 返回唯一的排版列表，以及数量
            same_bin_list = find_the_same_position(best_solution)

            draw_one_pic(best_solution, rate_list, width=2430,height=1210,
                        path='package_min_b' + data['bin_key'], border=1, num_list=same_bin_list, title=title,
                        shapes=data['shape_list'], empty_positions=data['empty_section'])

    else:
        print packer.error_info()


