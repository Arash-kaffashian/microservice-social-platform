from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from decouple import config
import requests

from .serializers import (
    LoginSerializer,
    CreatePostSerializer,
    UpdatePostSerializer,
    CreateUserSerializer,
    IdSerializer,
    EmailSerializer,
    UpdateUserSerializer)


""" gateway views (Microservice API Mapping) """


# services urls config
USER_SERVICE_URL = config("USER_SERVICE_URL")
POST_SERVICE_URL = config("POST_SERVICE_URL")

# internal_service_token config
INTERNAL_SERVICE_TOKEN = config("INTERNAL_SERVICE_TOKEN")



""" posts views """
# get all posts limited list
@api_view(["GET"])
def read_posts(request):
    url = f"{settings.POST_SERVICE_URL}/posts"

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
    url = f"{settings.POST_SERVICE_URL}/posts/{post_id}"

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
@extend_schema(request=UpdatePostSerializer,)
@api_view(["POST"])
def create_post(request):
    url = f"{POST_SERVICE_URL}/posts/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = UpdatePostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        url,
        json=serializer.validated_data,
        headers=headers
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# update one my posts by id
@extend_schema(request=UpdatePostSerializer,)
@api_view(["PATCH"])
def update_post(request, post_id):
    url = f"{POST_SERVICE_URL}/posts/{post_id}"
    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = CreatePostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.patch(
        url,
        json=serializer.validated_data,
        headers=headers
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# delete one of my posts
@api_view(["DELETE"])
def delete_post(request, post_id):
    url = f"{POST_SERVICE_URL}/posts/{post_id}"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.delete(
        url,
        headers=headers
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
    return Response(response_data, status=resp.status_code)



""" user views """
# login (session jwt token)
@extend_schema(request=LoginSerializer,responses={200: None},)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    url = f"{USER_SERVICE_URL}/auth/token"

    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    resp = requests.post(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
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

    try:
        resp = requests.get(
            url,
            headers=headers,
            params=params,
        )
    except requests.RequestException as e:
        return Response(
            {"error": "user_service is unreachable", "detail": str(e)},
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

# get one user by id
@api_view(["GET"])
def read_user(request, user_id):
    url = f"{USER_SERVICE_URL}/users/id={user_id}"

    headers = {
        "X-Internal-Token": INTERNAL_SERVICE_TOKEN
    }

    try:
        resp = requests.get(
            url,
            headers=headers,
        )
    except requests.RequestException as e:
        return Response(
            {"error": "user_service is unreachable", "detail": str(e)},
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

# get my profile
@api_view(["GET"])
def profile(request):
    url = f"{USER_SERVICE_URL}/users/profile"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        resp = requests.get(
            url,
            headers=headers,
        )
    except requests.RequestException as e:
        return Response(
            {"error": "user_service is unreachable", "detail": str(e)},
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

# register
@extend_schema(request=CreateUserSerializer,)
@api_view(["POST"])
def create_user(request):
    url = f"{USER_SERVICE_URL}/users/"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    resp = requests.post(
        url,
        json=serializer.validated_data,
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# delete my profile
@api_view(["DELETE"])
def delete_profile(request):
    url = f"{USER_SERVICE_URL}/users/me"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        resp = requests.delete(
            url,
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

# update my profile
@extend_schema(request=UpdateUserSerializer,)
@api_view(["PATCH"])
def update_profile(request):
    url = f"{USER_SERVICE_URL}/users/me"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = UpdateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.patch(
        url,
        json=serializer.validated_data,
        headers=headers
    )
    try:
        response_data = resp.json()
    except ValueError:
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
    return Response(response_data, status=resp.status_code)



""" settings views """
# change my email (and resend verification link to new email)
@extend_schema(request=EmailSerializer)
@api_view(["POST"])
def change_email(request):
    url = f"{USER_SERVICE_URL}/settings/change-email"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        url,
        json=serializer.validated_data,
        headers=headers,
    )
    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)
    return Response({"message": "your email successfully changed please check your email to verify it!"})

# resend verification link to my email
@api_view(["GET"])
def resend_verify(request):
    url = f"{USER_SERVICE_URL}/settings/resend-verify"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        url,
        headers=headers,
    )

    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)
    return Response({"message": "email verification resent"})

# verify verification link trigger
@api_view(["get"])
def verify_email(request, token):
    url = f"{USER_SERVICE_URL}/settings/verify?token={token}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.get(
        url,
        headers=headers,
    )
    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)
    return Response({"message": "your email verified!"})



""" admin panel urls"""
# promote to admin by id (superadmin only)
@extend_schema(request=IdSerializer)
@api_view(["POST"])
def create_admin(request):
    url = f"{USER_SERVICE_URL}/settings/admins"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = IdSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_id = serializer.validated_data["user_id"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        url,
        params={"user_id": user_id},
        headers=headers,
    )
    if resp.status_code != 200:
        return Response(resp.json(), status=resp.status_code)
    return Response({"message": "user promoted to admin"})

# admin delete_user by id (admin and superadmin only)
@api_view(["DELETE"])
def admin_delete_user(request, user_id):
    url = f"{USER_SERVICE_URL}/users/admin/users/{user_id}"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.delete(
        url,
        headers=headers
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}

    if resp.status_code == 200:
        response_data = {"user has been deleted"}
    return Response(response_data, status=resp.status_code)

# admin update_user by id (admin and superadmin only)
@extend_schema(request=UpdateUserSerializer,)
@api_view(["PATCH"])
def admin_update_user(request, user_id):
    url = f"{USER_SERVICE_URL}/users/admin/users/{user_id}"
    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    serializer = UpdateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.patch(
        url,
        json=serializer.validated_data,
        headers=headers
    )
    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}
    return Response(response_data, status=resp.status_code)

# admin delete_post by id (admin and superadmin only)
@api_view(["DELETE"])
def admin_delete_post(request, post_id):
    url = f"{POST_SERVICE_URL}/admin/posts/{post_id}"

    token = request.session.get("access_token")
    if not token:
        return Response({"detail": "Not logged in"}, status=401)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.delete(
        url,
        headers=headers
    )

    try:
        response_data = resp.json()
    except ValueError:  # JSONDecodeError
        response_data = {"detail": "Invalid response from post service", "text": resp.text}

    if resp.status_code == 200:
        response_data = {"post has been deleted"}
    return Response(response_data, status=resp.status_code)
