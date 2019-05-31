"""vue_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import xadmin
from vue_test.settings import MEDIA_ROOT
from rest_framework.authtoken import views
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from goods.views import GoodsListViewset, CategoryViewset, BannerViewset, IndexCategoryViewset
from users.views import SmsCodeViewset, UserViewset
from user_operation.views import *
from trade.views import *

router = DefaultRouter()
router.register(r'goods', GoodsListViewset, base_name="goods")
# 发送短信验证码
router.register(r'codes', SmsCodeViewset, base_name="codes")
#
router.register(r'users', UserViewset, base_name="users")
# 配置分组的url
router.register(r'categorys', CategoryViewset, base_name="categorys")
router.register(r'userfavs', UserFavViewset, base_name="userfavs")
router.register(r'messages', LeavingMessageViewset, base_name="messages")
router.register(r'address', AddressViewset, base_name="address")
# 购物车url
router.register(r'shopcarts', ShoppingCartViewset, base_name="shopcarts")
# 订单相关
router.register(r'orders', OrderViewset, base_name="orders")
# 轮播图
router.register(r'banners', BannerViewset, base_name="banners")
# 首页商品系列数据
router.register(r'indexgoods', IndexCategoryViewset, base_name="indexgoods")

# goods_list = GoodsListViewset.as_view({
#     'get': 'list',
# })
urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api_auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^', include(router.urls)),
    # 生成文档
    url(r'docs/', include_docs_urls(title="测试文档")),

    # drf自带token认证模式
    url(r'^api-token-auth', views.obtain_auth_token),

    # jwt token
    url(r'^login/', obtain_jwt_token)
]
