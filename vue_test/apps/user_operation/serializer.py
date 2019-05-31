from rest_framework import serializers
from .models import *
from rest_framework.validators import UniqueTogetherValidator

from goods.serializer import GoodsSerializer

# 手机号码正则表达式
REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"


class UserFavDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()
    class Meta:
        model = UserFav
        fields = ("goods", "id")


class UserFavSerializer(serializers.ModelSerializer):
    # 获取当前用户
    user = serializers.HiddenField(
            default=serializers.CurrentUserDefault()
         )
    class Meta:
        model = UserFav
        # 设置不能单用户不能重复操作过滤
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏"
            )
        ]
        fields = ('user', 'goods', 'id')


class LeavingSerializer(serializers.ModelSerializer):
    """
        留言序列化类
    """
    # 获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True)
    class Meta:
        model = UserLeavingMessage
        fields = ("user", "message_type", "subject", "message", "file", "add_time", "id")


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True)
    signer_mobile = serializers.CharField(max_length=11, min_length=11)

    def validate_mobile(self, mobile):
        # 手机号是否合法
        import re
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号非法")


    class Meta:
        model = UserAddress
        fields = ("id", "user", "province", "city", "district", "address", "signer_name", "add_time", "signer_mobile")
