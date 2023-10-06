from django.test import TestCase, Client
import json
# from loginManagement.models import User

# Create your tests here.
# class LoginManagementTestCase(TestCase):
#     def setUp(self) -> None:
#         user_data = {
#             "username": "defaultTest_user",
#             "email": "cpdd@gmail.com",
#             "password": 12121212
#         }
#         User.objects.create(**user_data)

#     def test_user_can_login(self):


class LoginManagementTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_can_register(self):
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

        res_data = json.loads(res.content)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res_data["info"], "创建用户成功!")

    def test_user_can_login(self):
        data_json = json.dumps({
            "username": "defaultTest_user",
            "password": 12121212
        })
        res = self.client.post(
            "/loginManagament/login/",
            data=data_json,
            content_type="application/json"
        )

        res_data = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_data["data"]["username"], "defaultTest_user")
