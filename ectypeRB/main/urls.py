from django.urls import path
from main.views import user, post, comment

app_name = "main"
urlpatterns = [
    path("user/homepage/", user.user_homepage, name="homepage"),
    path("user/follow/", user.follow_or_unfollow),
    path("user/following/", user.following_or_follower_list),
    path("user/post/control/", user.user_post_control),
    
    path("post/upload/", post.post_upload),
    path("post/detail/", post.post_detail),
    path("post/flow/", post.post_flow),
    path("post/delete/", post.post_delete),
    
    path("comment/create/", comment.comment_create),
    path("comment/flow/", comment.comment_flow),
    path("comment/delete/", comment.comment_delete)
]