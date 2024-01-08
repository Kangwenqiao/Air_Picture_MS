import unittest
from unittest.mock import MagicMock
from databaseutil import DatabaseUtil

class TestDatabaseUtil(unittest.TestCase):
    def setUp(self):
        # 初始化测试用的 DatabaseUtil 实例，并使用 MagicMock 代替数据库 session
        self.db_util = DatabaseUtil()
        self.db_util.session = MagicMock()

    def test_insert_or_update_object_detection(self):
        # 测试插入或更新目标检测数据
        detection_data = {'Image_Name': 'test.jpg', 'ymin': 0.1, 'xmin': 0.2, 'ymax': 0.3, 'xmax': 0.4}
        self.db_util.insert_or_update_object_detection(detection_data)
        # 断言 merge 和 commit 方法是否被调用了一次
        self.db_util.session.merge.assert_called_once()
        self.db_util.session.commit.assert_called_once()

    def test_insert_or_update_aircraft_detection(self):
        # 测试插入或更新飞机检测数据
        aircraft_data = {'Image_Name': 'test.jpg', 'confidence': 0.9, 'class_': 'F22'}
        self.db_util.insert_or_update_aircraft_detection(aircraft_data)
        # 断言 merge 和 commit 方法是否被调用了一次
        self.db_util.session.merge.assert_called_once()
        self.db_util.session.commit.assert_called_once()

    def test_print_aircraft_types_counts(self):
        # 模拟数据库中的预定数据，查询返回飞机类型和对应的数量
        self.db_util.session.query.return_value.group_by.return_value.all.return_value = [('F22', 2), ('B2', 3)]
        # 执行打印飞机类型和数量的方法
        result = self.db_util.print_aircraft_types_counts()
        # 期望的输出结果
        expected_output = "Aircraft Type: F22, Count: 2\nAircraft Type: B2, Count: 3"
        # 断言输出结果是否符合预期
        self.assertEqual(result, expected_output)

    def test_clear_aircraft_data_by_type(self):
        # 模拟数据库中有预定数据，清除指定飞机类型的数据
        aircraft_type = 'F22'
        self.db_util.clear_aircraft_data_by_type(aircraft_type)
        # 断言是否调用了查询和提交的方法
        self.db_util.session.query.assert_called()
        self.db_util.session.commit.assert_called_once()

    def test_clear_database(self):
        # 测试清空整个数据库
        self.db_util.clear_database()
        # 断言是否调用了查询和提交的方法
        self.db_util.session.query.assert_called()
        self.db_util.session.commit.assert_called_once()

    def test_query_by_image_name(self):
        # 模拟查询数据库中指定图片名称的数据
        image_name = 'datasets/train/images/f612a3684f5775b0c6ba643295a327cd.jpg'
        self.db_util.session.query.return_value.filter_by.return_value.all.return_value = [('F22',)]
        result = self.db_util.query_by_image_name(image_name)
        # 期望的输出结果
        expected_output = "F22"
        # 断言输出结果是否符合预期
        self.assertEqual(result, expected_output)

    def test_get_random_image_by_aircraft_type(self):
        # 模拟查询数据库中指定飞机类型的随机图片数据
        aircraft_type = 'F22'
        self.db_util.session.query.return_value.filter.return_value.all.return_value = [('datasets/train/images/f612a3684f5775b0c6ba643295a327cd.jpg', 0.1, 0.2, 0.3, 0.4, 'F22', 0.95)]
        result = self.db_util.get_random_image_by_aircraft_type(aircraft_type)
        # 期望的输出结果
        expected_output = ('datasets/train/images/f612a3684f5775b0c6ba643295a327cd.jpg', 0.1, 0.2, 0.3, 0.4, 'F22', 0.95)
        # 断言输出结果是否符合预期
        self.assertEqual(result, expected_output)

    def test_update_detection_results(self):
        # 测试更新指定图片名称的检测结果数据
        image_name = 'datasets/train/images/f612a3684f5775b0c6ba643295a327cd.jpg'
        self.db_util.update_detection_results(image_name, 0.1, 0.2, 0.3, 0.4, 0.95, 'F22')
        # 断言是否调用了查询和提交的方法
        self.db_util.session.query.assert_called()
        self.db_util.session.commit.assert_called_once()

    def test_check_user_credentials(self):
        # 模拟查询数据库中指定用户凭证的验证
        username = 'ncwu'
        password = '123456'
        self.db_util.session.query.return_value.filter_by.return_value.first.return_value = {'Username': 'user1', 'Role': 'Admin'}
        result = self.db_util.check_user_credentials(username, password)
        # 期望的输出结果
        expected_output = {'Username': 'user1', 'Role': 'Admin'}
        # 断言输出结果是否符合预期
        self.assertEqual(result, expected_output)

    def test_add_user(self):
        # 测试添加用户到数据库
        username = 'ncwu2'
        password = '123456'
        role = 'User'
        self.db_util.add_user(username, password, role)
        # 断言是否调用了添加和提交的方法
        self.db_util.session.add.assert_called_once()
        self.db_util.session.commit.assert_called_once()

    def test_close_connection(self):
        # 测试关闭数据库连接
        self.db_util.close_connection()
        # 断言是否调用了关闭连接的方法
        self.db_util.session.close.assert_called_once()

if __name__ == '__main__':
    # 运行单元测试
    unittest.main()
