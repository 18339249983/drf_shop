from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from user_operation.models import UserFav


@receiver(post_save, sender=UserFav)
def create_userfav(sender, instance=None, created=False, **kwargs):
    if created:
        goods = instance.goods
        goods.fav_num += 1
        goods.save()


@receiver(post_save, sender=UserFav)
def delete_userfav(sender, instance=None, created=False, **kwargs):
    if created:
        goods = instance.goods
        goods.fav_num -= 1
        goods.save()

