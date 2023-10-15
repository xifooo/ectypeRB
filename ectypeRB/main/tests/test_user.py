from django.test import TestCase, Client
import hashlib
from loginManagement.models import User
import json
from django.db import transaction


# Create your tests here.

class UserTestView(TestCase):
    @classmethod
    def setUpClass(cls):
        # 所有测试函数的共享部分
        cls.cls_atomics = cls._enter_atomics()
        data_list = [
            {
                "username": "defaultTest_user01",
                "email": "cpdd@gmail.com",
                "password": hashlib.sha256("12121212".encode()).hexdigest()
            },
            {
                "username": "defaultTest_user02",
                "email": "eg@gmail.com",
                "password": hashlib.sha256("13131313".encode()).hexdigest()
            }
        ]
        User.objects.create(**data_list[0])
        User.objects.create(**data_list[1])

    def setUp(self):
        # 在每个test函数运行前重新执行一次, 上一次执行的结果不保留
        self.client = Client()
        data_json = json.dumps({
            "username": "defaultTest_user01",
            "password": 12121212
        })
        res = self.client.post(
            "/loginManagement/login/",
            data=data_json,
            content_type="application/json"
        )
        res_data = json.loads(res.content)
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {res_data['data']['token']}"

    def test_user_homepage(self):
        res = self.client.get("/user/homepage/?user_id=1")
        res_data = json.loads(res.content)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res_data["data"]), 7)
        self.assertEqual(res_data["data"]["id"], 1)
        self.assertEqual(len(res_data["data"]["posts"]), 0)

    def test_user_do_follow(self):
        data = {
            "user_id": 2,
            "action": "follow",
            "method": "do"
        }
        res = self.client.patch(
            "/user/follow/",
            data=json.dumps(data),
            content_type="application/json"
        )
        res_data = json.loads(res.content)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_data["data"]["user"]["following_count"], 1)
        self.assertEqual(User.objects.get(id=1).following.count(), 1)

    @transaction.atomic
    def test_both(self):
        def test_user_follow_self():
            data = {
                "user_id": 1,
                "action": "follow",
                "method": "do"
            }
            res = self.client.patch(
                "/user/follow/",
                data=json.dumps(data),
                content_type="application/json"
            )
            res_data = json.loads(res.content)

            self.assertEqual(res.status_code, 400)
            self.assertEqual(res_data["error"], "can't follow your self")
            self.assertEqual(User.objects.get(id=1).following.count(), 0)

        def test_user_following_list():
            User.objects.get(id=1).following.add(User.objects.get(id=2))
            res = self.client.get(
                "/user/following/?types=following&offset=0&limit=10")
            res_data = json.loads(res.content)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res_data["data"]), 1)

        def test_user_follower_list():
            res = self.client.get(
                "/user/following/?types=follower&offset=0&limit=10")
            res_data = json.loads(res.content)
            user = User.objects.get(id=2)
            self.assertEqual(user.followings.all().count(), 1)

        def test_user_undo_follow():
            data = {
                "user_id": 2,
                "action": "follow",
                "method": "undo"
            }
            res = self.client.patch(
                "/user/follow/",
                data=json.dumps(data),
                content_type="application/json"
            )
            res_data = json.loads(res.content)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_data["data"]["user"]["following_count"], 0)
            self.assertEqual(User.objects.get(id=1).following.count(), 0)
        test_user_follow_self()
        test_user_following_list()
        test_user_follower_list()
        test_user_undo_follow()
