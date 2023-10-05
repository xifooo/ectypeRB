import datetime
import jwt
from ectypeRB.settings import SECRET_KEY
from django.http import JsonResponse


def generate_token(user):
    """
    generate_token: generate a token string.

    Args:
        user (user object): a instance of User model.

    Returns:
        str: token string.
    """
    payload = {
        "user-id": user.id,
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=3600, days=5)  # token 过期时间
    }
    headers = {
        "typ": "jwt",
        "alg": "HS256"
    }
    return jwt.encode(
        payload=payload,
        key=SECRET_KEY,
        algorithm="HS256",
        headers=headers
    )


def jwt_authorize(view_handler):
    def wrapper(req, *args, **kwargs):
        try:
            token = req.headers.get("Authorization")
            decoded_token = jwt.decode(token, SECRET_KEY, ["HS256"])
            # return view_handler(req, decoded_token, *args, **kwargs)
            return view_handler(req, *args, payload=decoded_token, **kwargs)

        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({"error": "登录身份过期"}, status=401)
        except jwt.DecodeError:
            return JsonResponse({"error": "身份认证失败"}, status=401)
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({"error": "非法token"}, status=401)

    return wrapper