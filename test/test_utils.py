import os
import random
import requests
from ate import utils
from ate import exception
from test.base import ApiServerUnittest

class TestUtils(ApiServerUnittest):

    def test_load_testcases_bad_filepath(self):
        testcase_file_path = os.path.join(os.getcwd(), 'test/data/demo')
        with self.assertRaises(exception.ParamsError):
            utils.load_testcases(testcase_file_path)

    def test_load_json_testcases(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'test/data/simple_demo_no_auth.json')
        testcases = utils.load_testcases(testcase_file_path)
        self.assertEqual(len(testcases), 2)
        testcase = testcases[0]["test"]
        self.assertIn('name', testcase)
        self.assertIn('request', testcase)
        self.assertIn('response', testcase)
        self.assertIn('url', testcase['request'])
        self.assertIn('method', testcase['request'])

    def test_load_yaml_testcases(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'test/data/simple_demo_no_auth.yml')
        testcases = utils.load_testcases(testcase_file_path)
        self.assertEqual(len(testcases), 2)
        testcase = testcases[0]["test"]
        self.assertIn('name', testcase)
        self.assertIn('request', testcase)
        self.assertIn('response', testcase)
        self.assertIn('url', testcase['request'])
        self.assertIn('method', testcase['request'])

    def test_parse_response_object_json(self):
        url = "http://127.0.0.1:5000/api/users"
        resp_obj = requests.get(url)
        parse_result = utils.parse_response_object(resp_obj)
        self.assertIn('status_code', parse_result)
        self.assertIn('headers', parse_result)
        self.assertIn('body', parse_result)
        self.assertIn('Content-Type', parse_result['headers'])
        self.assertIn('Content-Length', parse_result['headers'])
        self.assertIn('success', parse_result['body'])

    def test_parse_response_object_text(self):
        url = "http://127.0.0.1:5000/"
        resp_obj = requests.get(url)
        parse_result = utils.parse_response_object(resp_obj)
        self.assertIn('status_code', parse_result)
        self.assertIn('headers', parse_result)
        self.assertIn('body', parse_result)
        self.assertIn('Content-Type', parse_result['headers'])
        self.assertIn('Content-Length', parse_result['headers'])
        self.assertTrue(str, type(parse_result['body']))

    def test_diff_response_status_code_equal(self):
        status_code = random.randint(200, 511)
        resp_obj = requests.post(
            url="http://127.0.0.1:5000/customize-response",
            json={
                'status_code': status_code,
            }
        )

        expected_resp_json = {
            'status_code': status_code
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertFalse(diff_content)

    def test_diff_response_status_code_not_equal(self):
        status_code = random.randint(200, 511)
        resp_obj = requests.post(
            url="http://127.0.0.1:5000/customize-response",
            json={
                'status_code': status_code,
            }
        )

        expected_resp_json = {
            'status_code': 512
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertIn('value', diff_content['status_code'])
        self.assertIn('expected', diff_content['status_code'])
        self.assertEqual(diff_content['status_code']['value'], status_code)
        self.assertEqual(diff_content['status_code']['expected'], 512)

    def test_diff_response_headers_equal(self):
        resp_obj = requests.post(
            url="http://127.0.0.1:5000/customize-response",
            json={
                'headers': {
                    'abc': 123,
                    'def': 456
                }
            }
        )

        expected_resp_json = {
            'headers': {
                'abc': 123,
                'def': '456'
            }
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertFalse(diff_content)

    def test_diff_response_headers_not_equal(self):
        resp_obj = requests.post(
            url="http://127.0.0.1:5000/customize-response",
            json={
                'headers': {
                    'a': 123,
                    'b': '456',
                    'c': '789'
                }
            }
        )

        expected_resp_json = {
            'headers': {
                'a': '123',
                'b': '457',
                'd': 890
            }
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertEqual(
            diff_content['headers'],
            {
                'b': {'expected': '457', 'value': '456'},
                'd': {'expected': 890, 'value': None}
            }
        )

    def test_diff_response_body_equal(self):
        resp_obj = requests.post(
            url="http://127.0.0.1:5000/customize-response",
            json={
                'body': {
                    'success': True,
                    'count': 10
                }
            }
        )

        # expected response body is not specified
        expected_resp_json = {}
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertFalse(diff_content)

        # response body is the same as expected response body
        expected_resp_json = {
            'body': {
                'success': True,
                'count': '10'
            }
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertFalse(diff_content)

    def test_diff_response_body_not_equal_type_unmatch(self):
        resp_obj = requests.post(
            url="http://127.0.0.1:5000/customize-response",
            json={
                'body': {
                    'success': True,
                    'count': 10
                }
            }
        )

        # response body content type not match
        expected_resp_json = {
            'body': "ok"
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertEqual(
            diff_content['body'],
            {
                'value': {'success': True, 'count': 10},
                'expected': 'ok'
            }
        )

    def test_diff_response_body_not_equal_string_unmatch(self):
        resp_obj = requests.post(
            url="http://127.0.0.1:5000/customize-response",
            json={
                'body': "success"
            }
        )

        # response body content type matched to be string, while value unmatch
        expected_resp_json = {
            'body': "ok"
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertEqual(
            diff_content['body'],
            {
                'value': 'success',
                'expected': 'ok'
            }
        )

    def test_diff_response_body_not_equal_json_unmatch(self):
        resp_obj = requests.post(
            url="http://127.0.0.1:5000/customize-response",
            json={
                'body': {
                    'success': False
                }
            }
        )

        # response body is the same as expected response body
        expected_resp_json = {
            'body': {
                'success': True,
                'count': 10
            }
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertEqual(
            diff_content['body'],
            {
                'success': {
                    'value': False,
                    'expected': True
                },
                'count': {
                    'value': None,
                    'expected': 10
                }
            }
        )

    def test_load_foler_files(self):
        folder = os.path.join(os.getcwd(), 'test')
        files = utils.load_foler_files(folder)
        file1 = os.path.join(os.getcwd(), 'test', 'test_utils.py')
        file2 = os.path.join(os.getcwd(), 'test', 'data', 'demo_binds.yml')
        self.assertIn(file1, files)
        self.assertIn(file2, files)

    def test_load_testcases_by_path_files(self):
        testsets_list = []

        # absolute file path
        path = os.path.join(
            os.getcwd(), 'test/data/simple_demo_no_auth.json')
        testset_list = utils.load_testcases_by_path(path)
        self.assertEqual(len(testset_list), 1)
        self.assertEqual(len(testset_list[0]["testcases"]), 2)
        testsets_list.extend(testset_list)

        # relative file path
        path = 'test/data/simple_demo_no_auth.yml'
        testset_list = utils.load_testcases_by_path(path)
        self.assertEqual(len(testset_list), 1)
        self.assertEqual(len(testset_list[0]["testcases"]), 2)
        testsets_list.extend(testset_list)

        # list/set container with file(s)
        path = [
            os.path.join(os.getcwd(), 'test/data/simple_demo_no_auth.json'),
            'test/data/simple_demo_no_auth.yml'
        ]
        testset_list = utils.load_testcases_by_path(path)
        self.assertEqual(len(testset_list), 2)
        self.assertEqual(len(testset_list[0]["testcases"]), 2)
        self.assertEqual(len(testset_list[1]["testcases"]), 2)
        testsets_list.extend(testset_list)
        self.assertEqual(len(testsets_list), 4)

        for testset in testsets_list:
            for testcase in testset["testcases"]:
                self.assertIn('name', testcase)
                self.assertIn('request', testcase)
                self.assertIn('response', testcase)
                self.assertIn('url', testcase['request'])
                self.assertIn('method', testcase['request'])

    def test_load_testcases_by_path_folder(self):
        # absolute folder path
        path = os.path.join(os.getcwd(), 'test/data')
        testset_list_1 = utils.load_testcases_by_path(path)
        self.assertGreater(len(testset_list_1), 6)

        # relative folder path
        path = 'test/data/'
        testset_list_2 = utils.load_testcases_by_path(path)
        self.assertEqual(len(testset_list_1), len(testset_list_2))

        # list/set container with file(s)
        path = [
            os.path.join(os.getcwd(), 'test/data'),
            'test/data/'
        ]
        testset_list_3 = utils.load_testcases_by_path(path)
        self.assertEqual(len(testset_list_3), 2 * len(testset_list_1))

    def test_load_testcases_by_path_not_exist(self):
        # absolute folder path
        path = os.path.join(os.getcwd(), 'test/data_not_exist')
        testset_list_1 = utils.load_testcases_by_path(path)
        self.assertEqual(testset_list_1, [])

        # relative folder path
        path = 'test/data_not_exist'
        testset_list_2 = utils.load_testcases_by_path(path)
        self.assertEqual(testset_list_2, [])

        # list/set container with file(s)
        path = [
            os.path.join(os.getcwd(), 'test/data_not_exist'),
            'test/data_not_exist/'
        ]
        testset_list_3 = utils.load_testcases_by_path(path)
        self.assertEqual(testset_list_3, [])

    def test_parse_content_with_variables(self):
        content = "${var}"
        variables_binds = {
            "var": "abc"
        }
        result = utils.parse_content_with_variables(content, variables_binds)
        self.assertEqual(result, "abc")

        content = "123${var}456"
        variables_binds = {
            "var": "abc"
        }
        result = utils.parse_content_with_variables(content, variables_binds)
        self.assertEqual(result, "123abc456")

        content = "${var1}"
        variables_binds = {
            "var2": "abc"
        }
        with self.assertRaises(exception.ParamsError):
            utils.parse_content_with_variables(content, variables_binds)
