import json
from django.http import JsonResponse
from loginManagement.models import User
import hashlib
from utils.jwt_token import generate_token


# POST
def register(req):
    data = json.loads(req.body)
    email = data.get("email") or "123@default.com"
    # email, username二选一, password必须有
    if not (data.get("email") and data.get("username") and data.get("password")):
        return JsonResponse({"error": "email, username or password missing, please support correct data"}, status=400)
    
    # email 或 username 不能已被使用
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "该邮箱已被注册"}, status=409)
    elif User.objects.filter(username=data.get("username")).exists():
        return JsonResponse({"error": "该用户名已被注册"}, status=409)

    try:
        hashedPasswd = hashlib.sha256(
            str(data.get("password")).encode()
        ).hexdigest()
        user_data = {
            "email": data.get("email"),
            "username": data.get("username"),
            "password": hashedPasswd
        }
        User.objects.create(**user_data)
        return JsonResponse({"info": "创建用户成功!"})
    except Exception as e:
        print(e)
        return JsonResponse({"error": "创建用户失败"}, status=500)


# POST
def login(req):
    data = json.loads(req.body)
    # if data.get("email") and (not data.get("username")) and data.get("password"):
    # if not (data.get("email") or data.get("username") or data.get("password")):
    if not data.get("password") or not (data.get("username") or data.get("email")):
        return JsonResponse({
            "error": "email, username or password missing, please support correct data again."
        }, status=400)
    
    # email 和 username 只能用一个
    # email 优先于 username
    if data.get("email"):
        user = User.objects.filter(email__icontains=data.get("email")).first()
    elif (not data.get("email")) and data.get("username"):
        user = User.objects.filter(username__icontains=data.get("username")).first()
    passwd = data.get("password")
    hashedPasswd = hashlib.sha256(str(passwd).encode()).hexdigest()
    
    # 账户信息存在且密码正确
    if user and user.password == hashedPasswd:
        token = generate_token(user)
        user_data = {
            "id": user.id,
            "username": user.username,
            "signature": user.signature,
            "token": token
        }
        return JsonResponse({"data": user_data}, status=200)
    return JsonResponse({"error": "密码或邮箱不正确"}, status=400)
