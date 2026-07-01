from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from decouple import config
import requests

from . import serializers


""" gateway views (Microservice API Mapping) """


# services urls config
USER_SERVICE_URL = config("USER_SERVICE_URL")
POST_SERVICE_URL = config("POST_SERVICE_URL")
COMMENT_SERVICE_URL = config("COMMENT_SERVICE_URL")
MEDIA_SERVICE_URL = config("MEDIA_SERVICE_URL")

# internal_service_token config
INTERNAL_SERVICE_TOKEN = config("INTERNAL_SERVICE_TOKEN")



""" posts views """
# get all posts limited list
@api_view(["GET"])
def read_posts(request):
    url = f"{settings.POST_SERVICE_URL}/posts/"

    try:
        resp = requests.get(
            url,
            params=request.query_params,
            timeout=5,
        )
    except requests.RequestException as e:
        return Response(
            {"error": "post_service is unreachable", "detail": str(e)},
            status=502,
        )

    try:
        data = resp.json()
    except ValueError:
        return Response(
            {
                "error": "Invalid response from post_service",
                "status_code": resp.status_code,
                "raw": resp.text,
            },
            status=502,
        )

    return Response(data, status=resp.status_code)

# get all my posts limited list
@api_view(["GET"])
def read_my_posts(request):
    url = f"{settings.POST_SERVICE_URL}/myposts/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "skip": "0",
        "limit": "10"
    }

    try:
        resp = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=5,
        )
    except requests.RequestException as e:
        return Response(
            {"error": "post_service is unreachable", "detail": str(e)},
            status=502,
        )

    try:
        data = resp.json()
    except ValueError:
        return Response(
            {
                "error": "Invalid response from post_service",
                "status_code": resp.status_code,
                "raw": resp.text,
            },
            status=502,
        )

    return Response(data, status=resp.status_code)

# get one post by id
@api_view(["GET"])
def read_post(request, post_id):
    url = f"{settings.POST_SERVICE_URL}/posts/{post_id}/"

    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException as error:
        return Response(
            {
                "error": "post_service is unreachable",
                "detail": str(error),
            },
            status=503,
        )

    if resp.status_code == 404:
        return Response(
            {"detail": "Post not found"},
            status=404,
        )

    return Response(resp.json(), status=resp.status_code)

# create one post
@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'content': {'type': 'string'},
                'files': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        }
    }
)
@parser_classes([MultiPartParser, FormParser])
@api_view(["POST"])
def create_post(request):
    url = f"{POST_SERVICE_URL}/posts/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.CreatePostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        url,
        json={
            "title": serializer.validated_data["title"],
            "content": serializer.validated_data["content"],
        },
        headers=headers,
        timeout=5
    )
    if resp.status_code != 201 and resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)

    post_data = resp.json()
    post_id = post_data["id"]

    files = request.FILES.getlist("files")

    # storing files if it's exist and update post media urls
    if files:
        files_payload = [("files", (f.name, f, f.content_type)) for f in files]

        # file storage
        media_response = requests.post(
            f"{MEDIA_SERVICE_URL}/files/upload",
            params={"post_id": post_id},
            files=files_payload,
            headers={"Internal-Token": INTERNAL_SERVICE_TOKEN, "Authorization": f"Bearer {token}"}
        )

        # delete post record if file storage failed!
        if media_response.status_code != 200:
            requests.delete(f"{POST_SERVICE_URL}/posts/{post_id}", headers=headers)
            return Response({"error": "Media upload failed"}, status=500)

        media_urls = media_response.json().get("urls", [])
    else:
        media_urls = []

    # update post urls
    requests.patch(
        f"{POST_SERVICE_URL}/posts/{post_id}",
        json={"media_urls": media_urls},
        headers=headers,
        timeout=5
    )

    post_data["media_urls"] = media_urls
    return Response(post_data, status=201)

# update one of my posts by id
@extend_schema(request=serializers.UpdatePostSerializer,)
@api_view(["PATCH"])
def update_post(request, post_id):
    url = f"{POST_SERVICE_URL}/posts/{post_id}/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.UpdatePostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.patch(
        url,
        json=serializer.validated_data,
        headers=headers,
        timeout=5
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# delete one of my posts
@api_view(["DELETE"])
def delete_post(request, post_id):
    url = f"{POST_SERVICE_URL}/posts/{post_id}/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.delete(
        url,
        headers=headers,
        timeout=5
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
    return Response(response_data, status=resp.status_code)



""" comments views """
# get all comments
@api_view(["GET"])
def read_comments(request, post_id):
    url = f"{COMMENT_SERVICE_URL}/comments/{post_id}/"

    try:
        resp = requests.get(
            url,
            params=request.query_params,
            timeout=5,
        )
    except requests.RequestException as e:
        return Response(
            {"error": "comment_service is unreachable", "detail": str(e)},
            status=502,
        )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from comment service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# get one comment all replies
@api_view(["GET"])
def read_replies(request, comment_id):
    url = f"{COMMENT_SERVICE_URL}/comments/replies/{comment_id}/"

    try:
        resp = requests.get(
            url,
            params=request.query_params,
            timeout=5,
        )
    except requests.RequestException as e:
        return Response(
            {"error": "comment_service is unreachable", "detail": str(e)},
            status=502,
        )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from comment service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# create one comment for one post
@extend_schema(request=serializers.CreateCommentSerializer,)
@api_view(["POST"])
def create_comment(request):
    url = f"{COMMENT_SERVICE_URL}/comments/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.CreateCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    post_id = serializer.validated_data["post_id"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.get(
        f"{POST_SERVICE_URL}/posts/{post_id}",
        timeout=5
    )

    if resp.status_code == 404:
        return Response({"detail": "post not found"}, status=404)

    resp = requests.post(
        url,
        json=serializer.validated_data,
        headers=headers,
        timeout=5
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from comment service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# create one reply for one comment
@extend_schema(request=serializers.CreateReplySerializer,)
@api_view(["POST"])
def create_reply(request):
    url = f"{COMMENT_SERVICE_URL}/comments/reply/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.CreateReplySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    post_id = serializer.validated_data["post_id"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.get(
        f"{POST_SERVICE_URL}/posts/{post_id}",
        timeout=5
    )

    if resp.status_code == 404:
        return Response({"detail": "post not found"}, status=404)

    resp = requests.post(
        url,
        json=serializer.validated_data,
        headers=headers,
        timeout=5
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from comment service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# update one of my comments/replies by id
@extend_schema(request=serializers.UpdateCommentSerializer,)
@api_view(["PATCH"])
def update_comment(request, comment_id):
    url = f"{COMMENT_SERVICE_URL}/comments/{comment_id}/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.UpdateCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.patch(
        url,
        json=serializer.validated_data,
        headers=headers,
        timeout=5
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from comment service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# delete one of my comments and its replies by id
@api_view(["DELETE"])
def delete_comment(request, comment_id):
    url = f"{COMMENT_SERVICE_URL}/comments/delete/id={comment_id}/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.delete(
        url,
        headers=headers,
        timeout=5
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from comment service", "text": resp.text}
    return Response(response_data, status=resp.status_code)


    return Response(response_data, status=resp.status_code)



""" avatar views """
# get avatar
@api_view(["GET"])
def read_avatar(request, owner_id):
    url = f"{MEDIA_SERVICE_URL}/avatar/id={owner_id}/"

    headers = {
        "X-Internal-Token": INTERNAL_SERVICE_TOKEN
    }

    resp = requests.get(
        url,
        headers=headers,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from media service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# set one avatar record and user.avatar to default avatar
@api_view(["PUT"])
def set_default(request):
    url = f"{MEDIA_SERVICE_URL}/avatar/set_default/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.put(
        url,
        headers=headers,
        timeout=5,
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from media service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# change avatar
@extend_schema(request={"multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "format": "binary"
                }
            },
            "required": ["file"]
        }})
@api_view(["PUT"])
@parser_classes([MultiPartParser, FormParser])
def update_avatar(request):
    url = f"{MEDIA_SERVICE_URL}/avatar/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.UpdateAvatarSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    file_obj = request.FILES.get("file")

    resp = requests.put(
        url,
        headers=headers,
        files={
            "file": (
                file_obj.name,
                file_obj,
                file_obj.content_type
            )
        },
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from media service", "text": resp.text}
    return Response(response_data, status=resp.status_code)



""" files views """
# get one post medias
@api_view(["GET"])
def read_medias(request, post_id):
    url = f"{MEDIA_SERVICE_URL}/files/post={post_id}/"

    resp = requests.get(
        url,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from media service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# get one media
@api_view(["GET"])
def read_media(request, media_id):
    url = f"{MEDIA_SERVICE_URL}/files/media={media_id}/"


    resp = requests.get(
        url,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from media service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# change one media
@extend_schema(request={"multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "format": "binary"
                }
            },
            "required": ["file"]
        }})
@parser_classes([MultiPartParser, FormParser])
@api_view(["PATCH"])
def update_media(request, media_id):
    url = f"{MEDIA_SERVICE_URL}/files/media={media_id}/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.UpdateAvatarSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Internal-Token": INTERNAL_SERVICE_TOKEN
    }

    file_obj = request.FILES.get("file")

    resp = requests.patch(
        url,
        headers=headers,
        files={
            "file": (
                file_obj.name,
                file_obj,
                file_obj.content_type
            )
        },
        timeout = 5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from media service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# delete one media (hard delete)
@api_view(["DELETE"])
def delete_media(request, media_id):
    url = f"{MEDIA_SERVICE_URL}/files/media={media_id}/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Internal-Token": INTERNAL_SERVICE_TOKEN
    }

    resp = requests.delete(
        url,
        headers=headers,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from media service", "text": resp.text}
    return Response(response_data, status=resp.status_code)



""" user views """
# login (session jwt token)
@extend_schema(request=serializers.LoginSerializer,responses={200: None},)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    url = f"{USER_SERVICE_URL}/auth/token/"

    serializer = serializers.LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    resp = requests.post(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5
    )

    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)

    request.session["access_token"] = resp.json()["access_token"]
    return Response({"message": "logged in"})

# get all users limited list
@api_view(["GET"])
def read_users(request):
    url = f"{USER_SERVICE_URL}/users/"

    headers = {
        "X-Internal-Token": INTERNAL_SERVICE_TOKEN
    }

    params = {
        "skip": "0",
        "limit": "10"
    }

    resp = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from user service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# get one user by id
@api_view(["GET"])
def read_user(request, user_id):
    url = f"{USER_SERVICE_URL}/users/id={user_id}/"

    headers = {
        "X-Internal-Token": INTERNAL_SERVICE_TOKEN
    }

    resp = requests.get(
        url,
        headers=headers,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from user service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# get my profile
@api_view(["GET"])
def profile(request):
    url = f"{USER_SERVICE_URL}/users/profile/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.get(
        url,
        headers=headers,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from user service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# register
@extend_schema(request=serializers.CreateUserSerializer,)
@api_view(["POST"])
def create_user(request):
    url = f"{USER_SERVICE_URL}/users/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    resp = requests.post(
        url,
        json=serializer.validated_data,
        timeout=5
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from user service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# delete my profile
@api_view(["DELETE"])
def delete_profile(request):
    url = f"{USER_SERVICE_URL}/users/me/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.delete(
        url,
        headers=headers,
        timeout=5,
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from user service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# update my profile
@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "nickname": {"type": "string"},
                "image": {"type": "string", "format": "binary"},
            }
        }
    }
)
@parser_classes([MultiPartParser, FormParser])
@api_view(["PATCH"])
def update_profile(request):
    url = f"{USER_SERVICE_URL}/users/me/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.UpdateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    payload = serializer.validated_data.copy()

    if 'image' in payload:
        del payload['image']

    headers = {"Authorization": f"Bearer {token}"}

    # update avatar image if it"s exist
    if "image" in request.FILES:
        image_file = request.FILES["image"]

        media_resp = requests.put(
            f"{MEDIA_SERVICE_URL}/avatar/",
            headers=headers,
            files={"file": (image_file.name, image_file, image_file.content_type)},
            timeout=10
        )

        if media_resp.status_code == 200:
            image_url = media_resp.json().get("url")
            payload["image_url"] = image_url
        else:
            return Response(
                {"detail": "Failed to upload image to media service"},
                status=media_resp.status_code
            )

    # update user record
    resp = requests.patch(
        url,
        json=payload,
        headers=headers,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:
        response_data = {"detail": "Invalid response from user service", "text": resp.text}

    return Response(response_data, status=resp.status_code)



""" settings views """
# change my email (and resend verification link to new email)
@extend_schema(request=serializers.EmailSerializer)
@api_view(["POST"])
def change_email(request):
    url = f"{USER_SERVICE_URL}/settings/change-email/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        url,
        json=serializer.validated_data,
        headers=headers,
        timeout=5
    )
    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)
    return Response({"message": "your email successfully changed please check your email to verify it!"})

# resend verification link to my email
@api_view(["GET"])
def resend_verify(request):
    url = f"{USER_SERVICE_URL}/settings/resend-verify/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        url,
        headers=headers,
        timeout=5
    )

    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)
    return Response({"message": "email verification resent"})

# verify verification link trigger
@api_view(["get"])
def verify_email(request, token):
    url = f"{USER_SERVICE_URL}/settings/verify?token={token}/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.get(
        url,
        headers=headers,
        timeout=5
    )
    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)
    return Response({"message": "your email verified!"})



# promote to admin by id (superadmin only)
@extend_schema(request=serializers.IdSerializer)
@api_view(["POST"])
def create_admin(request):
    url = f"{USER_SERVICE_URL}/settings/admins/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.IdSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_id = serializer.validated_data["user_id"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        url,
        params={"user_id": user_id},
        headers=headers,
        timeout=5
    )

    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)
    return Response({"message": "user promoted to admin"})

# admin delete_user by id (admin and superadmin only)
@api_view(["DELETE"])
def admin_delete_user(request, user_id):
    url = f"{USER_SERVICE_URL}/users/admin/users/{user_id}/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.delete(
        url,
        headers=headers,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from user service", "text": resp.text}

    if resp.status_code == 200:
        response_data = {"user has been deleted"}
    return Response(response_data, status=resp.status_code)

# admin update_user by id (admin and superadmin only)
@extend_schema(request=serializers.UpdateUserSerializer,)
@api_view(["PATCH"])
def admin_update_user(request, user_id):
    url = f"{USER_SERVICE_URL}/users/admin/users/{user_id}/"
    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = serializers.UpdateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.patch(
        url,
        json=serializer.validated_data,
        headers=headers,
        timeout=5
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
        response_data = {"detail": "Invalid response from user service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

    return Response(response_data, status=resp.status_code)

# admin delete_post by id (admin and superadmin only)
@api_view(["DELETE"])
def admin_delete_post(request, post_id):
    url = f"{POST_SERVICE_URL}/admin/posts/{post_id}/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.delete(
        url,
        headers=headers,
        timeout=5
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}

    if resp.status_code == 200:
        response_data = {"post has been deleted"}
    return Response(response_data, status=resp.status_code)

