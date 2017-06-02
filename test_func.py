# encoding=utf8
from package import PackerSolution
import unittest

# 执行测试的类
class PackerTestCaseTrue(unittest.TestCase):
    def setUp(self):
        shape_data = "A 582 58 22;B 732 58 20;C 770 450.7 17"
        bin_data = u"A 双面胡桃木哑光25mm 2430 1210 1 0;B 双面白布纹哑光18mm 2430*1210*18;C 单面胡桃木哑光9mm 2430 1210 1"
        BORDER = 5  # 产品间的间隔, 算在损耗中
        self.packer = PackerSolution(shape_data, bin_data, border=BORDER)

    def tearDown(self):
        self.packer = None

    def test_validation(self):
        self.assertTrue(self.packer.is_valid())

    def test_get_bins_key(self):
        self.assertEqual(len(self.packer.get_bins_key()), 3)
        self.assertEqual(self.packer.get_bins_key()[0], 'A')

    def test_get_bin_data(self):
        self.assertEqual(len(self.packer.get_bin_data('A')), 7)
        self.assertEqual(self.packer.get_bin_data('A', key='width'), 2430)
        self.assertEqual(self.packer.get_bin_data('A', key='height'), 1210)
        self.assertEqual(self.packer.get_bin_data('A', key='is_texture'), 1)
        self.assertEqual(self.packer.get_bin_data('A', key='shape_num')[0], 22)

    def test_find_solution(self):
        res = self.packer.find_solution()
        self.assertEqual(len(res), 3)
        self.assertLess(res[2]['rate'], 1)
        self.assertLess(res[2]['algo_id'], 60)

        res = self.packer.find_solution(algo_list=[0])
        self.assertEqual(res[2]['algo_id'], 0)


class PackerTestCaseFalse(unittest.TestCase):

    def tearDown(self):
        self.packer = None

    def test_validation(self):
        shape_data = "A 582 58 22;B 732 58 20;D 770 450 17"
        bin_data = u"A 双面胡桃木哑光25mm 2430 1210 1 0;B 双面白布纹哑光18mm 2430*1210*18;C 单面胡桃木哑光9mm 2430 1210 1"
        BORDER = 5  # 产品间的间隔, 算在损耗中
        self.packer = PackerSolution(shape_data, bin_data, border=BORDER)
        self.assertFalse(self.packer.is_valid())

        shape_data = "A 582 58 22;B 732 58 20;D 770 450 17"
        bin_data = u"A 双面胡桃木哑光25mm 2430 1210 1 0;B 双面白布纹哑光18mm 2430*1210*18;C 单面胡桃木哑光9mm 2430 1210 1"
        self.packer = PackerSolution(shape_data, bin_data)
        self.assertFalse(self.packer.is_valid())

        shape_data = "A 582 58 22;B 732 58 20"
        bin_data = u"A 双面胡桃木哑光25mm 2430*1210*2 否;B 双面白布纹哑光18mm 2430*1210*18 是;C 单面胡桃木哑光9mm 2430 1210 1"
        self.packer = PackerSolution(shape_data, bin_data)
        self.assertTrue(self.packer.is_valid())

        shape_data = "A 582 58 22;B 732.4 58.5 20"
        bin_data = u"A 双面胡桃木哑光25mm 2430*1210*2 否;B 双面白布纹哑光18mm 2430*1210*18 是;C 单面胡桃木哑光9mm 2430 1210 1"
        self.packer = PackerSolution(shape_data, bin_data, border=10)
        self.assertTrue(self.packer.is_valid())
        self.packer.find_solution(algo_list=[0])

        shape_data = '[{"SkuCode":"32050052","Length":548.0,"Width":397.0,"Amount":11}]'
        bin_data = u'[{"SkuCode":"32050052","ItemName":"三聚氰胺板-双面仿古白哑光单保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050519","ItemName":"三聚氰胺板-双面仿古白哑光双保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050093","ItemName":"三聚氰胺板-双面仿古白哑光(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050038","ItemName":"三聚氰胺板-双面仿古白哑光单保(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050076","ItemName":"三聚氰胺板-双面仿古白哑光(5mm)","SkuName":"2440*1220*5mm","HasGrain":"否"},{"SkuCode":"32050434","ItemName":"三聚氰胺板-2#8834双面仿橡胶木哑光(12mm)","SkuName":"2440*1220*12mm","HasGrain":"是"},{"SkuCode":"32010003","ItemName":"中纤板(E1)-B(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32010004","ItemName":"中纤板(E1)-B(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050051","ItemName":"三聚氰胺板-双面仿古白哑光(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"}]'
        bins_num = '[{"SkuCode":"32050052","Amount":2,"SkuName":"1440*720*25mm"},{"SkuCode":"32050052","Amount":1,"SkuName":"740*720*25mm"}]'
        self.packer = PackerSolution(shape_data, bin_data, bins_num=bins_num)
        self.assertTrue(self.packer.is_valid())
        self.assertEqual(self.packer.get_bin_data('32050052', key='is_texture'), 0)
        self.packer.find_solution(algo_list=[40])

        shape_data = '[{"SkuCode":"32050052","Length":548.5,"Width":397.0,"Amount":11}]'
        bin_data = u'[{"SkuCode":"32050052","ItemName":"三聚氰胺板-双面仿古白哑光单保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050519","ItemName":"三聚氰胺板-双面仿古白哑光双保(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050093","ItemName":"三聚氰胺板-双面仿古白哑光(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050038","ItemName":"三聚氰胺板-双面仿古白哑光单保(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32050076","ItemName":"三聚氰胺板-双面仿古白哑光(5mm)","SkuName":"2440*1220*5mm","HasGrain":"否"},{"SkuCode":"32050434","ItemName":"三聚氰胺板-2#8834双面仿橡胶木哑光(12mm)","SkuName":"2440*1220*12mm","HasGrain":"是"},{"SkuCode":"32010003","ItemName":"中纤板(E1)-B(18mm)","SkuName":"2440*1220*18mm","HasGrain":"否"},{"SkuCode":"32010004","ItemName":"中纤板(E1)-B(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"},{"SkuCode":"32050051","ItemName":"三聚氰胺板-双面仿古白哑光(25mm)","SkuName":"2440*1220*25mm","HasGrain":"否"}]'
        self.packer = PackerSolution(shape_data, bin_data, empty_section_min_height=10, empty_section_min_size=1000)
        self.assertTrue(self.packer.is_valid())
        self.assertEqual(self.packer.get_bin_data('32050052', key='is_texture'), 0)
        self.packer.find_solution(algo_list=[40])

# 测试
if __name__ == "__main__":
    unittest.main()

