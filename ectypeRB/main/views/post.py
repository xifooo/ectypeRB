import json
from django.http import JsonResponse
from main.models import Post, Image
from utils.aux import (
    convert_timezone,
    image_serialize,
    limit_querySet,
    posts_serialize
)
import os
import hashlib
from ectypeRB.settings import TIME_ZONE, MEDIA_ROOT
from django.core.files.storage import default_storage


# POST
def post_upload(req, *args, **kwargs):
    payload = kwargs.get("payload")
    user_id = payload.get("user-id")
    data = json.loads(req.body)
    if not data.get("title"):
        return JsonResponse({"error": "the post's title missing"}, status=400)
    post_data = {
        "title": data.get("title"),
        "content": data.get("content"),
        "user_id": int(user_id)
    }
    post = Post.objects.create(**post_data)
    if not post:
        return JsonResponse({"error": "错误操作"}, status=500)

    files = req.FILES.getlist("file")
    if not len(files):
        return JsonResponse({
            "data": {
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "created_at": convert_timezone(post.created_at, TIME_ZONE)
                }
            }
        }, status=201)
    for f in files:
        f_extension = os.path.splitext(f.name)[1]
        md5 = hashlib.md5(f.read()).hexdigest()
        f_name = f"{md5}{f_extension}"
        f_path = f"{MEDIA_ROOT}/post/{post.id}/{f_name}"

        with Image.open(f) as i:
            img_height = i.height
            img_width = i.width
        img_data = {
            "image_path": f_path,
            "post": post,
            "height": img_height,
            "width": img_width
        }
        Image.objects.create(**img_data)
        default_storage(f_path, f)
    imgs = Image.objects.filter(post_id=post.id).all()
    serialied_imgs = image_serialize(imgs)
    return JsonResponse({
        "data": {
            "post": {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": convert_timezone(post.created_at, TIME_ZONE),
                "images": list(serialied_imgs)
            }
        }
    }, status=201)

# def post_update(req, *args, **kwargs):
    # # 处理文件
    # import typing
    # import hashlib
    # def calc_md5_list(files:typing.Iterable):
    #     file_md5_list = []
    #     for f in files:
    #         f_content = f.read()
    #         md5 = hashlib.md5(f_content).hexdigest()
    #         file_md5_list.append(md5)
    #     return file_md5_list
    # lst = [hashlib.md5(f.read()).hexdigest() for f in files]
    # ...


# GET
def post_detail(req, *args, **kwargs):
    post_id = req.GET.get("post_id")
    post = Post.objects.filter(id=int(post_id)).first()
    imgs = Image.objects.filter(post_id=int(post_id)).all()
    if not len(imgs):
        post_data = {
            "id": post_id,
            "title": post.title,
            "content": post.content,
            "created_at": convert_timezone(post.created_at, TIME_ZONE)
        }
    serialized_imgs = image_serialize(imgs)
    return JsonResponse({
        "data": {
            "post": {
                **post_data,
                "images": list(serialized_imgs)
            }
        }
    }, status=200)


# GET
def post_flow(req, *args, **kwargs):
    payload = kwargs.get("payload")
    user_id = payload.get("user-id")
    offset, limit = req.GET.get("offset") or 0, req.GET.get("limit") or 10
    posts = Post.objects.all()
    limited_posts = limit_querySet(posts, offset=int(offset), limit=int(limit))
    serialized_posts = posts_serialize(limited_posts)
    return JsonResponse({
        "data": {
            "post": serialized_posts
        }
    }, status=200)
    
    
# DELETE xxx
# 删 post ：1.删内容 2.删文件 
def post_delete(req, *args, **kwargs):
    post_id = req.GET.get("post_id")
    if not post_id:
        return JsonResponse({"error": "params post_id missing"}, status=400)
    
    post = Post.objects.filter(id=int(post_id)).first()
    if not post:
        return JsonResponse({"error": "objective post not found"}, status=404)
    
    payload = kwargs.get("payload")
    user_id = payload.get("user-id")
    if post.user.id != int(user_id):
        return JsonResponse({"error": "you are not the post owner"}, status=401)
    # xxx
    post.user.remove(user_id)
    post.save()
    return JsonResponse({"info": "successfully delete the post"}, status=200)