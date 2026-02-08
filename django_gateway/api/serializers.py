from rest_framework import serializers


""" DRF Serializers for swagger and Routers input """

# login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# create_post
class CreatePostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()

# update_post
class UpdatePostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()

# update_user
class UpdateUserSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50)
    image_url = serializers.CharField(max_length=255)

# create_user
class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(style={'input_type': 'password'})
    email = serializers.EmailField(max_length=100)
    nickname = serializers.CharField(max_length=50)
    image_url = serializers.CharField(max_length=255)

# id
class IdSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

# email
class EmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
