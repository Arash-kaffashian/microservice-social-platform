from django.urls import path

from . import views


""" Main URLs """


urlpatterns = [
    # posts urls
    path("posts/", views.read_posts),
    path("posts/me", views.read_my_posts),
    path("posts/<int:post_id>", views.read_post),
    path("posts/create/", views.create_post),
    path("posts/update/<int:post_id>", views.update_post),
    path("posts/delete/<int:post_id>", views.delete_post),

    # comments urls
    path("comments/<int:post_id>", views.read_comments),
    path("comments/replies/<int:comment_id>", views.read_replies),
    path("comments/create/", views.create_comment),
    path("comments/reply/", views.create_reply),
    path("comments/update/<int:comment_id>", views.update_comment),
    path("comments/delete/<int:comment_id>", views.delete_comment),

    # avatar urls
    path("avatar/id=<owner_id>", views.read_avatar),
    path("avatar/set_default", views.set_default),
    path("avatar/me", views.update_avatar),

    # files urls
    path("files/post=<post_id>", views.read_medias),
    path("files/media=<media_id>", views.read_media),
    path("files/update/media=<media_id>", views.update_media),
    path("files/delete/media=<media_id>", views.delete_media),

    # users urls
    path("login/", views.login),
    path("users/", views.read_users),
    path("users/id=<int:user_id>", views.read_user),
    path("users/profile/", views.profile),
    path("users/register/", views.create_user),
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
