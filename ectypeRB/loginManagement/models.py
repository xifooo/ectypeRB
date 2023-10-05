from django.db import models


class User(models.Model):
    username = models.CharField(max_length=128, verbose_name="用户名", null=False)
    email = models.CharField(max_length=32, verbose_name="邮箱", null=False)
    password = models.CharField(max_length=256, verbose_name="密码", null=False)
    signature = models.CharField(
        max_length=256, verbose_name="个性签名", default="这个人很烂, 什么也没留下", null=True)
    avatar = models.CharField(
        max_length=256, verbose_name="头像", null=False,
        default="http://localhost:8000/static/img/avatar/defaultAvatar.jpg")
    following = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="followings")

    def __str__(self):
        return f"{self.username} - {self.email}"
