from django.test import TestCase, Client
import json


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        data_json = json.dumps({
            "username": "defaultTest_user",
            "email": "cpdd@gmail.com",
            "password": 12121212
        })
        res = self.client.post(
            "/loginManagement/register/",
            data=data_json,
            content_type="application/json"
        )

    def test_user_can_register(self):
        data_json = json.dumps({
            "username": "Frankie",
            "email": "wordnewnew@email.com",
            "password": "12121212"
        })
        res = self.client.post(
            "/loginManagement/register/",
            data=data_json,
            content_type="application/json"
        )

        res_data = json.loads(res.content)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res_data["info"], "创建用户成功!")

    def test_error_register_noUsername(self):
        data_json = json.dumps({
            "email": "email@gmail.com",
            "password": 12121212
        })
        res = self.client.post(
            "/loginManagement/register/",
            data=data_json,
            content_type="application/json"
        )
        res_data = json.loads(res.content)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res_data["error"],
            "email, username or password missing, please support correct data"
        )

    def test_error_register_existedUsername(self):
        data_json = json.dumps({
            "username": "defaultTest_user",
            "email": "cccddd@gmail.com",
            "password": 156123
        })
        res = self.client.post(
            "/loginManagement/register/",
            data=data_json,
            content_type="application/json"
        )
        res_data = json.loads(res.content)
        self.assertEqual(res.status_code, 409)
        self.assertEqual(
            res_data["error"],
            "该用户名已被注册"
          )

    def test_user_can_login(self):
        data_json = json.dumps({
            "username": "defaultTest_user",
            "password": 12121212
        })
        res = self.client.post(
            "/loginManagement/login/",
            data=data_json,
            content_type="application/json"
        )
        res_data = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_data["data"]["username"], "defaultTest_user")

    def test_error_login_noPassword(self):
        data_json = json.dumps({
            "username": "defaultTest_user"
        })
        res = self.client.post(
            "/loginManagement/login/",
            data=data_json,
            content_type="application/json"
        )

        res_data = json.loads(res.content)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res_data["error"],
            "email, username or password missing, please support correct data again."
        )

