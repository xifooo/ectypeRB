from django.test import TestCase, Client
import hashlib
from loginManagement.models import User
from main.models import Post
import json
from django.db import transaction
from ectypeRB.settings import BASE_DIR
from django.core.files import File
import os


class PostTestView(TestCase):
    @classmethod
    def setUpClass(cls):
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
    def test_post_all_success(self):
        def test_post_upload_success():
            data_json = json.dumps({
                "title": "世界语",
                "content": """La mondo kiu ni naskis ne plu ekzistas.La klimato, la specoj kaj la naturaj retoj kolapsis."""
            })
            file_dir = f"{BASE_DIR}/main/tests/static_for_test"
            files = [
                File(
                    open(os.path.join(file_dir, fname), "rb")
                ) for fname in os.listdir(file_dir)
            ]
            # 不行(open对象)
            # files = [
            #     open(
            #         os.path.join(file_dir, fname), "rb"
            #     ).read()
            #     for fname in os.listdir(file_dir)
            # ]
            # 不行(open对象)
            # files = []
            # for fname in os.listdir(file_dir):
            #     f = open(os.path.join(file_dir, fname), 'rb')
            #     files.append(('file', f))

            res = self.client.post(
                "/post/upload/",
                data={
                    "file": files,
                    "form-data": data_json
                },
                format="multipart"
            )
            self.assertEqual(res.status_code, 201)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["post"]), 5)
            self.assertEqual(res_data["data"]["post"]["title"], "世界语")
            self.assertEqual(len(res_data["data"]["post"]["images"]), 2)

        def test_post_noImage_upload_success():
            data = {
                "title": "misaki",
                "content": "nanami"
            }
            res = self.client.post(
                "/post/upload/",
                {
                    "form-data": json.dumps(data)
                }
            )
            self.assertEqual(res.status_code, 201)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["post"]), 4)
            self.assertEqual(res_data["data"]["post"]["title"], "misaki")
            self.assertEqual(res_data["data"]["post"].get("images"), None)

        def test_post_detail_success():
            res = self.client.get("/post/detail/?post_id=2")
            self.assertEqual(res.status_code, 200)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["post"]), 5)
            self.assertEqual(res_data["data"]["post"]["id"], "2")
            self.assertEqual(len(res_data["data"]["post"]["images"]), 2)

            res = self.client.get("/post/detail/?post_id=1")
            self.assertEqual(res.status_code, 200)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["post"]), 4)
            self.assertEqual(res_data["data"]["post"]["id"], "1")
            self.assertIsNone(res_data.get("data").get("post").get("images"))

        def test_post_flow_success():
            res = self.client.get("/post/flow/?offset=0&limit=10")
            self.assertEqual(res.status_code, 200)

            res_data = json.loads(res.content)
            self.assertEqual(len(res_data["data"]["post"]), 3)

        def test_post_delete_success():
            res = self.client.get("/post/delete/?post_id=2")
            self.assertEqual(res.status_code, 200)

            res_data = json.loads(res.content)
            self.assertEqual(res_data["info"], "successfully delete the post")
            
            res = self.client.get("/post/detail/?post_id=2")
            self.assertEqual(res.status_code, 404)

            res_data = json.loads(res.content)
            self.assertEqual(res_data["error"], "objective post not found")
        
        test_post_upload_success()
        test_post_noImage_upload_success()
        test_post_flow_success()
        test_post_detail_success()
        test_post_delete_success()
