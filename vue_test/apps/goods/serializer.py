from django.db.models import Q
from rest_framework import serializers

from goods.models import *


class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ("image",)


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = GoodsImageSerializer(many=True)

    class Meta:
        model = Goods
        # fields = ('name', 'click_num', 'market_price', 'add_time')
        fields = "__all__"
    # def create(self, validated_data):
    #     return Goods.objects.create(**validated_data)


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    """
    宣传图标
    """

    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexAd
        fields = "__all__"


class IndexCategorySerializer(serializers.ModelSerializer):
    """
    主页分组显示页面
    """
    brands = BrandSerializer(many=True)
    goods = serializers.SerializerMethodField()  # 对相关字段序列化表进行设定
    sub_cat = CategorySerializer2(many=True)
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self, obj):
        """
            获取广告图片
        :param obj:
        :return:
        """
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            goods_ins = ad_goods[0].goods
            # 上下文中有request就会有完整的图片路由
            goods_json = GoodsSerializer(goods_ins, many=False, context={'request': self.context['request']}).data  # 一定要返回data
        return goods_json

    def get_goods(self, obj):
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__parent_category_id=obj.id) | Q(
            category__parent_category__parent_category_id=obj.id))
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = "__all__"
