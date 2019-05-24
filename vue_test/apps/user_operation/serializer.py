from rest_framework import serializers
from .models import *
from rest_framework.validators import UniqueTogetherValidator


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
