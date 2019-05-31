from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
import re
from datetime import datetime, timedelta
from rest_framework.validators import UniqueValidator

from .models import VerifyCode

# 手机号码正则表达式
REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"


class SmsSerialize(serializers.Serializer):
    """
    发送验证码， 只能传递一个手机号所以只能使用serializer自定义
    """
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """
        验证手机号码
        :param data:
        :return:
        """
        # 手机是否注册
        if User.object.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")

        # 验证手机号是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")

        # 验证发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送未超过60秒")

        return mobile


class UserRegSerialize(serializers.ModelSerializer):
    """
    注册用户
    """
    code = serializers.CharField(max_length=4, min_length=4, write_only=True,
                                 error_messages={
                                    "blank": "请输入验证码",
                                    "requird": "请输入验证码",
                                 },
                                 help_text="验证码")
    username = serializers.CharField(required=True, allow_blank=False, validators = [
            UniqueValidator(
                queryset=User.objects.all(),
                message="用户名重复",
            )])
    password = serializers.CharField(
        style={"input_type": 'password'}, label="密码", write_only=True
    )

    def create(self, validated_data):
        # 创建密码加密  validated_data传递的是序列化后的数据
        user = super(UserRegSerialize, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    # validate_**** 加字段名，对但字段进行验证
    def validate_code(self, code):
        # initial_data前端使用post传递过来的数据都包含在这个里面
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            last_records = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_records.add_time:
                raise serializers.ValidationError("验证码过期")
            if last_records.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        """
        对验证完成的所有字段进行自定义过滤处理
        """
        attrs['mobile'] = attrs['username']
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", 'password')


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化
    """
    class Meta:
        model = User
        fields = ("username", "gender", "birthday", "email", "mobile")