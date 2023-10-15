from django.test import TestCase, Client
import hashlib
from loginManagement.models import User
from main.models import Post
import json
from django.db import transaction


class CommentTestView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cls_atomics = cls._enter_atomics()
        user_data = {
            "username": "defaultTest_user01",
            "email": "cpdd@gmail.com",
            "password": hashlib.sha256("12121212".encode()).hexdigest()
        }
        User.objects.create(**user_data)
        post_data = {
            "title": "Lorem Ipsum",
            "content": """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
            Cras eu sem suscipit, sagittis nulla vitae, 
            fringilla quam. Donec suscipit justo tellus, 
            id convallis enim imperdiet ac. Duis congue, 
            justo pellentesque cursus vestibulum, 
            lectus nisl tincidunt quam, eu consequat lorem lectus a quam.""",
            "user_id": 1
        }
        Post.objects.create(**post_data)

    def setUp(self):
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

    @transaction.atomic
    def test_comment_create_flow_delete_success(self):
        def test_main_comment_create_success():
            data_json = json.dumps({
                "content": "very good, love from China.",
                "post_id": 1
            })
            res = self.client.post(
                "/comment/create/",
                data=data_json,
                content_type="application/json"
            )
            self.assertEqual(res.status_code, 201)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["comment"]), 3)
            self.assertEqual(res_data["data"]["comment"]
                             ["content"], "very good, love from China.")

        def test_sub_comment_create_success():
            data_json = json.dumps({
                "content": "very bad, hate from Jap.",
                "post_id": 1,
                "parent_comment_id": 1
            })
            res = self.client.post(
                "/comment/create/",
                data=data_json,
                content_type="application/json"
            )
            self.assertEqual(res.status_code, 201)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["comment"]), 3)
            self.assertEqual(res_data["data"]["comment"]
                             ["content"], "very bad, hate from Jap.")

        def test_main_comment_flow_success():
            res = self.client.get(
                "/comment/flow/?types=main&post_id=1&offset=0&limit=10")
            self.assertEqual(res.status_code, 200)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["comments"]), 1)
            self.assertEqual(res_data["data"]["comments"]
                             [1], "very good, love from China.")

        def test_sub_comment_flow_success():
            res = self.client.get(
                "/comment/flow/?types=replies&post_id=1&offset=0&limit=10")
            self.assertEqual(res.status_code, 200)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["comments"]), 0)
            self.assertEqual(res_data["data"]["comments"]
                             [1], "very bad, hate from Jap.")

        def test_sub_comment_delete():
            res = self.client.delete(
                "/comment/?comment_id=2"
            )
            self.assertEqual(res.status_code, 200)
            res_data = json.loads(res.content)
            self.assertEqual(res_data["info"], "successfully delete comment")
        test_main_comment_create_success()
        test_sub_comment_create_success()
        test_main_comment_flow_success()
        test_sub_comment_flow_success()
        test_sub_comment_delete()
