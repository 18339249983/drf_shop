from django.shortcuts import render
from .models import *
from rest_framework import mixins
from rest_framework import generics
from .serializer import GoodsSerializer, CategorySerializer, BannerSerializer, IndexCategorySerializer
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from rest_framework import filters
from .filters import GoodsFilter
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


# class GoodsListView(APIView):
#     """
#     List all snippets, or create a new snippet.
#     """
    # def get(self, request, format=None):
    #     goods = Goods.objects.all()[:10]
    #     goods_serializer = GoodsSerializer(goods, many=True)
    #     return Response(goods_serializer.data)


    # def post(self, request, format=None):
    #     serializer = GoodsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 商品分页
# class GoodsPagination(PageNumberPagination):
# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 10
#     # 前端动态传递参数控制当页显示条数
#     page_size_query_param = 'page_size'
#     page_query_param = "page"
#     max_page_size = 100


# class GoodsListView(generics.ListAPIView):
class GoodsListViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
        商品列表展示, 分页、过滤、搜索、排序
    """
    # 限速配置
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer

    # pagination_class = GoodsPagination
    # authentication_classes = (TokenAuthentication,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_class = GoodsFilter
    search_fields = ('name', 'goods_brief', 'goods_desc')
    ordering_fields = ('sold_num', 'add_time')

    def retrieve(self, request, *args, **kwargs):
        # 商品点击数  重载该方法对数量进行更新
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    # def get_queryset(self):
    #     queryset = Goods.objects.all()
    #     price_min = self.request.query_params.get("price_min", 0)
    #     if price_min:
    #         queryset = queryset.filter(shop_price__gt=int(price_min))
    #     return queryset
class CategoryViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品列表数据
        Retrieve,查看单个详情
    """
    queryset = GoodsCategory.objects.all()
    serializer_class = CategorySerializer


class BannerViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取轮播图列表
    """
    serializer_class = BannerSerializer
    queryset = Banner.objects.all().order_by("index")


class IndexCategoryViewset(viewsets.ModelViewSet):
    """
    首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True)
    serializer_class = IndexCategorySerializer