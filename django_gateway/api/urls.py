from django.urls import path

from . import views


""" main URLs """


urlpatterns = [
    # posts urls
    path("posts/", views.read_posts),
    path("posts/me", views.read_my_posts),
    path("posts/<int:post_id>", views.read_post),
    path("create_post/", views.create_post),
    path("update_post/<int:post_id>", views.update_post),
    path("delete_post/<int:post_id>", views.delete_post),

    # users urls
    path("login/", views.login),
    path("users/", views.read_users),
    path("users/id=<int:user_id>", views.read_user),
    path("profile/", views.profile),
    path("register/", views.create_user),
    path("users/delete_profile", views.delete_profile),
    path("users/update_profile", views.update_profile),

    # settings urls
    path("settings/change_email", views.change_email),
    path("settings/resend_verify", views.resend_verify),
    path("settings/verify/<str:token>", views.verify_email),

    # admin panel urls
    path("admin_panel/create_admin", views.create_admin),
    path("admin_panel/delete_user/<int:user_id>", views.admin_delete_user),
    path("admin_panel/update_user/<int:user_id>", views.admin_update_user),
    path("admin_panel/delete_post/<int:post_id>", views.admin_delete_post),
]