from django.shortcuts import render
from random import choice
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serialize import *
from utils.yunpian import *
from vue_test.settings import APIKEY
from .models import VerifyCode
from utils.permissions import IsOwnerOrReadOnly



User = get_user_model()
# Create your views here


class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username)|Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerialize

    def generate_code(self):
        """
        生成四位数字的验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # 参数异常直接会抛出异常
        serializer.is_valid(raise_exception=True)
        # 取出serialize中定义的参数
        mobile = serializer.validated_data["mobile"]

        yun_pian = YunPian(APIKEY)

        code = self.generate_code()

        sms_status = yun_pian.send_sms(code=code, mobile=mobile)
        if sms_status['code'] != 0:
            return Response({
                'mobile': sms_status['msg'],
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                'mobile': mobile
            }, status=status.HTTP_201_CREATED)


class UserViewset(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    """
    read:
        查看当前用户信息
    create:
        注册用户
    """
    serializer_class = UserRegSerialize
    # queryset = User.objects.all()
    authentication_class = (authentication.SessionAuthentication,JSONWebTokenAuthentication) # 动态设置权限这种暂不可取

    def get_serializer_class(self):
        # 动态加载序列化类  区别显示不同的用户详情
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerialize
        else:
            return UserRegSerialize

    def get_permissions(self):
        # 只有使用了viewset才会有这个action  动态区别权限
        if self.action == "retriave":
            return [permissions.IsAuthenticated]
        elif self.action == "create":
            return []
        else:
            return []

    def create(self, request, *args, **kwargs):
        """
        重载函数，再注册完成后返回生成的token完成注册后即登录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # 使用jwt取出生成的token
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        # 可以自定义添加想要返回的任何参数
        re_dict["token"] = jwt_encode_handler(payload)

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        """
        返回当前用户
        :return:
        """
        return self.request.user

    def perform_create(self, serializer):
        # 返回的是该序列化的实例对象，这里返回的是User对象
        return serializer.save()