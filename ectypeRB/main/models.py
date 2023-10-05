from django.db import models
from loginManagement.models import User
# import os


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=128, verbose_name="标题", null=False)
    content = models.CharField(max_length=3000, verbose_name="内容", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    # def delete(self, *args, **kwargs):
    #     """
    #     delete del the post relative imgs
    #     """
    #     self.imgs.all().delete()
    #     files = os.listdir()
    #     for item in files:
    #         if item.startswith(f"{self.id}-"):
    #             os.remove(os.path.join(f"{SYSTEM_PATH}/post/", item))
    #     super().delete(*args, **kwargs)


class Image(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="imgs")
    image_path = models.CharField(max_length=256, verbose_name="图片位置")
    height = models.IntegerField(default=0, verbose_name="图片高度")
    width = models.IntegerField(default=0, verbose_name="图片宽度")


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments", null=False)
    user = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name="comments",default="账户已注销", null=False)
    content = models.CharField(max_length=256, verbose_name="评论内容", null=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, related_name="replies", null=True)

User.favorites = models.ManyToManyField(Post, blank=True, related_name="favoritesPosts")
User.collection = models.ManyToManyField(Post, blank=True, related_name="collectedPosts")