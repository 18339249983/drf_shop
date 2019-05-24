from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from .serializer import *
# Create your views here.


class UserFavViewset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    用户收藏功能
    """
    queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer

