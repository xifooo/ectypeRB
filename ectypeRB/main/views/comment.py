import json
from django.http import JsonResponse
from main.models import Comment
from utils.aux import (
    convert_timezone,
    limit_querySet,
)
from ectypeRB.settings import TIME_ZONE


# POST
def comment_create(req, *args, **kwargs):
    payload = kwargs.get("payload")
    user_id = payload.get("user-id")
    data = json.loads(req.body)
    post_id, content = data.get("post_id"), data.get("content")
    if not (post_id and content):
        return JsonResponse({"error": "params post_id or content missing"}, status=400)
    comment_data = {
        "content": content,
        "user_id": int(user_id),
        "post_id": int(post_id),
        "parent_comment_id": data.get("parent_comment_id")
    }
    comment = Comment.objects.create(**comment_data)
    return JsonResponse({
        "data": {
            "comment": {
                "id": comment.id,
                "content": comment.content,
                "created_at": convert_timezone(comment.created_at, TIME_ZONE)
            }
        }
    }, status=201)


# GET
def comment_flow(req, *args, **kwargs):
    post_id = req.GET.get("post_id")
    typ = req.GET.get("types") or "main"
    if typ.upper() == "MAIN":
        comments = Comment.objects.filter(post_id=int(post_id))
    elif typ.upper() == "REPLIES":
        parent_comment_id = req.GET.get("parent_comment_id")
        if not parent_comment_id:
            return JsonResponse({"error": "params parent_comment_id missing"}, status=400)
        comments = Comment.objects.filter(
            parent_comment_id=int(parent_comment_id))
    else:
        return JsonResponse({"error": "types unsupported"}, status=405)
    if not comments:
        return JsonResponse({"error": "objective comments not found"}, status=404)
    offset, limit = req.GET.get("offset") or 0, req.GET.get("limit") or 10
    limited_comments = limit_querySet(
        comments, offset=int(offset), limit=int(limit))
    return JsonResponse({
        "data": {
            "comments": list(limited_comments)
        }
    }, status=200)


# DELETE
def comment_delete(req, *args, **kwargs):
    payload = kwargs.get("payload")
    user_id = payload.get("user-id")
    comment_id = req.GET.get("comment_id")
    if not comment_id:
        return JsonResponse({"error": "params comment_id missing"}, status=400)
    comment = Comment.objects.filter(id=int(comment_id)).first()
    user_id = int(user_id)
    if user_id != comment.user.id:
        return JsonResponse({"error": "you are not the comment owner"}, status=401)
    # # 若是子评论
    # if not comment.parent_comment:
    #     comment.replies.all().delete()
    # # 若是主评论
    # else:
    #     comment.replies.all().delete()
    #     comment.parent_comment.replies.remove(comment)
    comment.delete()
    return JsonResponse({"info": "successfully delete comment"}, status=200)
    
