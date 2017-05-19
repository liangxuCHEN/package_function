# encoding=utf8
from package import PackerSolution
import unittest


# 执行测试的类
class PackerTestCaseTrue(unittest.TestCase):
    def setUp(self):
        shape_data = "A 582 58 22;B 732 58 20;C 770 450 17"
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

# 测试
if __name__ == "__main__":
    unittest.main()
