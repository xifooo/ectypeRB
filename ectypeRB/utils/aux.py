import pytz
from ectypeRB.settings import TIME_ZONE

def convert_timezone(dt_obj, tz_str):
    target_tz = pytz.timezone(tz_str)
    converted_dt = dt_obj.astimezone(target_tz)
    return converted_dt.strftime("%Y-%m-%d %H:%M")


def limit_querySet(querySet, offset=0, limit=10):
    if 0 <= offset < querySet.count():
        return querySet.order_by("-id")[offset:limit]
    return []


def posts_serialize(posts):
    for p in posts:
        data = {
            "id": p.id,
            "title": p.title,
            "load": False,
            "created_at": convert_timezone(p.created_at, TIME_ZONE),
            "user": {
                "id": p.user.id,
                "username": p.user.username,
                "avatar": p.user.avatar
            }
        }
        imgs = p.imgs.all()
        if imgs:
            data = {
                **data,
                "img": imgs[0].image_path,
                "img_info": {
                    "height": imgs[0].height,
                    "width": imgs[0].width
                }
            }
        yield data


def following_serialize(following):
    for u in following:
        data = {
            "id": u.id,
            "username": u.username,
            "signature": u.signature,
            "avatar": u.avatar,
        }
        yield data


def image_serialize(imgs):
    for img in imgs:
        data = {
            "id": img.id,
            "height": img.height,
            "width": img.width,
            "path": img.image_path
        }
        yield data


def comments_serialize(comments):
    for c in comments:
        data = {
            "id": c.id,
            "content": c.content,
            "created_at": convert_timezone(c.created_at, TIME_ZONE),
            "user": {
                "id": c.user.id,
                "username": c.user.username,
                "avatar": c.user.avatar
            }
        }
        yield data