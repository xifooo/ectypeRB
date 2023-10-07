from django.http import JsonResponse
from loginManagement.models import User
from utils.aux import posts_serialize, limit_querySet, following_serialize
import json
from main.models import Post
# from django.core.files.storage import default_storage


# GET
def user_homepage(req, *args, **kwargs):
    user_id = req.GET.get("user_id")
    if not user_id:
        return JsonResponse({"error": "params user_id missing"}, status=400)
    user = User.objects.filter(id=int(user_id)).first()
    if not user:
        return JsonResponse({"error": "objective user not found"}, status=404)
    user_data = {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "signature": user.signature,
        "following_count": user.following.count(),
        "follower_count": user.followings.count(),
        # "postsCount": user.posts.count(),
        "posts": []
    }
    if user.posts.all().count():
        offset, limit = req.GET.get("offset") or 0, req.GET.get("limit") or 10
        posts = limit_querySet(user.posts.all(), offset=int(offset), limit=int(limit))
        serialized_posts = list(posts_serialize(posts))
        user_data = {
            **user_data,
            "posts": serialized_posts
        }
    return JsonResponse({"data": user_data}, status=200)


# # GET
# def user_profile(req, *args, **kwargs):
#     user_id = req.GET.get("user_id")
#     if not user_id:
#         return JsonResponse({"error": "params user_id missing"}, status=400)
#     user = User.objects.filter(id=int(user_id)).first()
#     if not user:
#         return JsonResponse({"error": "objective user not found"}, status=404)
#     user_data = {
#         "id": user.id,
#         "username": user.username,
#         "avatar": user.avatar,
#         "signature": user.signature,
#         "followingCount": user.following.count(),
#         "followerCount": user.followings.count(),
#         "postsCount": user.posts.count()
#     }
#     return JsonResponse({"data": user_data}, status=200)


# PATCH
def follow_or_unfollow(req, *args, **kwargs):
    payload = kwargs.get("payload")
    logged_user_id = payload.get("user-id")
    data = json.loads(req.body)
    user_id = data.get("user_id")
    if not user_id:
        return JsonResponse({"error": "necessary params missing"}, status=400)
    if user_id == logged_user_id:
        return JsonResponse({"error": "can't follow your self"}, status=400)
    logged_user = User.objects.filter(id=logged_user_id).first()
    user = User.objects.filter(id=user_id).first()
    if not user:
        return JsonResponse({"error": "objective user not found"}, status=404)

    action, method = data.get("action"), data.get("method")
    if not (action and method):
        return JsonResponse({"error": "necessary params missing"}, status=400)
    if action.upper() == "FOLLOW":
        if method.upper() == "DO":
            logged_user.following.add(user)
            logged_user.save()
        elif method.upper() == "UNDO":
            logged_user.following.remove(user)
            logged_user.save()
        else:
            return JsonResponse({"error": "method unsupported"}, status=405)
    else:
        return JsonResponse({"error": "action unsupported"}, status=405)
    return JsonResponse({
        "data": {
            "user": {
                "id": logged_user_id,
                "following_count": logged_user.following.count()
            }
        }
    }, status=200)

# # GET following or follower
# def user_following_list(req, *args, **kwargs):
#     payload = kwargs.get("payload")
#     user_id = payload.get("user-id")
#     user = User.objects.filter(id=user_id).first()
#     user_following = user.following.all()
#     if not user_following.count():
#         return JsonResponse({"data": []}, status=200)
#     offset, limit = req.GET.get("offset") or 0, req.GET.get("limit") or 10
#     limited_user_following = limit_querySet(user_following, offset=offset, limit=limit)
#     serialized_user_following = list(following_serialize(limited_user_following))
#     return JsonResponse({"data": serialized_user_following}, status=200)


# GET following or follower list
def following_or_follower_list(req, *args, **kwargs):
    payload = kwargs.get("payload")
    user_id = payload.get("user-id")
    typ = req.GET.get("types")
    if not typ:
        return JsonResponse({"error": "necessary params missing"}, status=400)

    user = User.objects.filter(id=int(user_id)).first()
    if typ.upper() == "FOLLOWING":
        user_list = user.following.all()
    elif typ.upper() == "FOLLOWER":
        user_list = user.followings.all()
    if not user_list.count():
        return JsonResponse({"data": []}, status=200)
    offset, limit = req.GET.get("offset") or 0, req.GET.get("limit") or 10
    limited_user_list = limit_querySet(user_list, offset=int(offset), limit=int(limit))
    serialized_user_list = list(following_serialize(limited_user_list))
    return JsonResponse({"data": serialized_user_list}, status=200)


# PATCH
def user_post_control(req, *args, **kwargs):
    payload = kwargs.get("payload")
    user_id = payload.get("user-id")
    data = json.loads(req.body)
    post_id = data.get("post_id")
    action, method = data.get("action"), data.get("method")
    if not (post_id and action and method):
        return JsonResponse({"error": "necessary params missing"}, status=400)
    post = Post.objects.filter(id=int(post_id)).first()
    if not post:
        return JsonResponse({"error": "objective post not found "}, status=404)
    user = User.objects.filter(id=user_id).first()
    action, method = action.upper(), method.upper()
    if action == "LIKE":
        if method == "DO":
            user.favorites.add(post)
            user.save()
        elif method == "UNDO":
            user.favorites.remove(post)
            user.save()
        else:
            return JsonResponse({"error": "method unsupported"}, status=405)
    elif action == "COLLECT":
        if method == "DO":
            user.collection.add(post)
            user.save()
        elif method == "UNDO":
            user.collection.remove(post)
            user.save()
        else:
            return JsonResponse({"error": "method unsupported"}, status=405)
    else:
        return JsonResponse({"error": "action unsupported"}, status=405)
    return JsonResponse({
        "data": {
            "user": {
                "id": user_id,
                "favorites": user.favorites.count(),
                "collection": user.collection.count()
            }
        }
    }, status=200)