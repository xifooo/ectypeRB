from django.http import HttpResponseForbidden
import jwt
from ectypeRB.settings import SECRET_KEY
# from django.urls import reverse


# whitelist_urls = [
#     reverse("loginManagement.login"),
#     reverse("register"),
#     reverse("homepage")
# ]
whilelist = {
    "loginManagement": ["login", "register"],
    "main": []
}

class JWTMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        # path = request.path_info

        # if path in whitelist_urls:
        #     return None
        app_name = request.resolver_match.app_name
        view_func_name = view_func.__name__
        if whilelist.get(app_name) and view_func_name in whilelist.get(app_name):
            return None

        token = request.META.get("HTTP_AUTHORIZATION", "").split("Bearer ")[1]

        if not token:
            return HttpResponseForbidden({"message": "Auth token is missing"})

        try:
            payload = jwt.decode(token, SECRET_KEY, ["HS256"])
        except:
            return HttpResponseForbidden({"message": "Invalid auth token"})

        view_kwargs["payload"] = payload
        return None
