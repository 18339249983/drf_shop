import time

from rest_framework import serializers
from goods.models import Goods
from .models import *
from goods.serializer import GoodsSerializer


"""
    添加购物车功能，保证数据库中的每个用户收藏同类商品的数据始终为一条，如果重复提交则进行数量叠加
    添加数量，需要先判断库存数量是否够用
    在此文件夹中使用create方法是由于数据库定义了双字段唯一，如果在视图中使用create方法则会导致字段验证时就会报错
    继承了serializer就要重写create和update或者delete等的方法
"""
class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)
    class Meta:
        model = ShoppingCart
        fields = "__all__"

class ShopCartSerialize(serializers.Serializer):
    # 获取当前用户 隐藏该用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, label='数量', min_value=1,
                                    error_messages={
                                        'min_value': "商品数量不能小于一",
                                        'required': "请选择购买数量"
                                    })
    goods = serializers.PrimaryKeyRelatedField(queryset=Goods.objects.all())

    def create(self, validated_data):
        # 序列化类中user放在全局上下文中，视图中则在request中
        user = self.context["request"].user
        nums = validated_data['nums']
        goods = validated_data['goods']

        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        if existed:
            existed = existed[0]
            good_num = existed.nums + nums
            if good_num <= Goods.objects.get(name=goods).goods_num:
                existed.nums = good_num
                existed.save()
            else:
                raise serializers.ValidationError("超出库存数量")
        else:
            existed = ShoppingCart.objects.create(**validated_data)
        return existed

    def update(self, instance, validated_data):
        # 修改商品数量
        instance.nums = validated_data['nums']
        goods = validated_data['goods']
        if instance.nums <= Goods.objects.get(name=goods).goods_num:
            instance.save()
        else:
            raise serializers.ValidationError("超出库存数量")
        return instance


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)
    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerialezer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)
    class Meta:
        model = OrderInfo
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    # 获取当前用户 隐藏该用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    nonce_str = serializers.CharField(read_only=True)

    def generate_order_sn(self):
        # 当前时间+user+随机数
        import random
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random.randint(10, 99))
        return order_sn

    def validate(self, attrs):
        # 直接在序列化类中添加字段值
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"