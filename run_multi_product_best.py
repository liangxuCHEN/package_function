# encoding=utf8
import json
from package import PackerSolution
from package_tools import use_rate

"""
    通过不同比例组合产品，找到最佳组合
    data
    'bin_key': bin_key,
    'solution': best_solution,
    'empty_section': empty_positions,
    'rate': best_rate,
    'algo_id': best_packer,
    'bins_list': bins_list,
"""

def merge_bin_data(data1, data2):
    """
    合并相同的板材
    :param data1:
    :param data2:
    :return:
    """
    res = json.loads(data1)
    data2 = json.loads(data2)
    for d2 in data2:
        has_sku = False
        for dr in res:
            if d2['SkuCode'] == dr['SkuCode']:
                has_sku = True
                break
        if not has_sku:
            res.append(d2)

    return json.dumps(res)


def merge_shape_data(data1, data2, data1_num, data2_num):
    """
    按照不同的比例组合产品，默认没有重复的组件
    :param data1:
    :param data2:
    :param data1_num:
    :param data2_num:
    :return:
    """
    data1 = json.loads(data1)
    data2 = json.loads(data2)
    res = list()
    for d1 in data1:
        d1['Amount'] = d1['Amount'] * data1_num
        for d2 in data2:
            if d2['Amount'] != 0 and d1['Length'] == d2['Length'] and d1['Width'] == d2['Width'] and d1['SkuCode'] == d2['SkuCode']:
                d1['Amount'] += d2['Amount'] * data2_num
                d2['Amount'] = 0
                continue
    # 合并数据
    for d2 in data2:
        if d2['Amount'] != 0:
            d2['Amount'] = d2['Amount'] * data2_num
            res.append(d2)
    res += data1
    return json.dumps(res)


if __name__ == '__main__':
    # 床
    shape_data_1 = '[{"SkuCode":"32050038","Length":1294.0,"Width":398.0,"Amount":9},{"SkuCode":"32050093","Length":1444.0,"Width":296.0,"Amount":9},{"SkuCode":"32010004","Length":1056.0,"Width":279.0,"Amount":9},{"SkuCode":"32010004","Length":1200.0,"Width":330.0,"Amount":9},{"SkuCode":"32050051","Length":2010.0,"Width":128.0,"Amount":18},{"SkuCode":"32050052","Length":1444.0,"Width":456.0,"Amount":9},{"SkuCode":"32050052","Length":1444.0,"Width":163.0,"Amount":9}]'
    bin_data_1 = '[{"SkuCode":"32050038","ItemName":"三聚氰胺板-双面仿古白哑光单保(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050093","ItemName":"三聚氰胺板-双面仿古白哑光(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32010004","ItemName":"中纤板(E1)-B(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050051","ItemName":"三聚氰胺板-双面仿古白哑光(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050052","ItemName":"三聚氰胺板-双面仿古白哑光单保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"}]'
    # 床头柜
    bin_data_2 = '[{"SkuCode":"32050093","ItemName":"三聚氰胺板-双面仿古白哑光(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050076","ItemName":"三聚氰胺板-双面仿古白哑光(5mm)","SkuName":"2440*1220*5mm","HasGrain":"否"},{"SkuCode":"32050434","ItemName":"三聚氰胺板-2#8834双面仿橡胶木哑光(12mm)","SkuName":"2440*1220*12mm","HasGrain":"是"},{"SkuCode":"32050038","ItemName":"三聚氰胺板-双面仿古白哑光单保(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050519","ItemName":"三聚氰胺板-双面仿古白哑光双保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050052","ItemName":"三聚氰胺板-双面仿古白哑光单保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"}]'
    shape_data_2 = '[{"SkuCode":"32050093","Length":319.0,"Width":136.0,"Amount":10},{"SkuCode":"32050076","Length":406.0,"Width":291.0,"Amount":20},{"SkuCode":"32050434","Length":396.0,"Width":110.0,"Amount":20},{"SkuCode":"32050434","Length":295.0,"Width":110.0,"Amount":40},{"SkuCode":"32050038","Length":484.0,"Width":190.0,"Amount":20},{"SkuCode":"32050076","Length":396.0,"Width":456.0,"Amount":10},{"SkuCode":"32050093","Length":386.0,"Width":362.0,"Amount":20},{"SkuCode":"32050093","Length":446.0,"Width":75.0,"Amount":10},{"SkuCode":"32050519","Length":516.0,"Width":397.0,"Amount":10},{"SkuCode":"32050052","Length":516.0,"Width":397.0,"Amount":10},{"SkuCode":"32050038","Length":340.0,"Width":55.0,"Amount":10}]'

    for num_1 in range(1, 4):
        for num_2 in range(num_1+1, 5):
            # 合并数据
            shape_data = merge_shape_data(shape_data_1, shape_data_2, num_1, num_2)
            bin_data = merge_bin_data(bin_data_1, bin_data_2)

            for num_pic in range(1, 30):
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

                        with open('bed_DI1B_DIA_mix_2.txt', 'a+') as f:
                            f.write('%d,%d,%d,%s,%d,%s\n' % (num_1, num_2, num_pic, data['bin_key'],
                                                             len(best_solution), str(data['rate'])))

                else:
                    print packer.error_info()

                print(">>>> num1:%d, num2:%d, num_pic:%d " % (num_1, num_2, num_pic))


