from django.urls import path
from loginManagement import views


app_name = "loginManagement"
urlpatterns = [
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register")
]
