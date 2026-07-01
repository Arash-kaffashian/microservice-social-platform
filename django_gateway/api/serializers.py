from rest_framework import serializers


""" DRF Serializers for swagger and Routers input """


# login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


# create_post
class CreatePostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    content = serializers.CharField(max_length=255)
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

# create_user
class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(style={'input_type': 'password'})
    email = serializers.EmailField(max_length=100)
    nickname = serializers.CharField(max_length=50)

# create_comment
class CreateCommentSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    content = serializers.CharField(max_length=255)

# create_reply
class CreateReplySerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    content = serializers.CharField(max_length=255)
    parent_id = serializers.IntegerField()

# update_post
class UpdatePostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    content = serializers.CharField(max_length=255)

# update_user
class UpdateUserSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50, required=False)
    image = serializers.FileField(required=False)

# update_comment
class UpdateCommentSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=255)

# update_media
class UpdateAvatarSerializer(serializers.Serializer):
    file = serializers.FileField()


# id
class IdSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

# email
class EmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
