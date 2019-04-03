from uuid import uuid4
import django.utils.timezone as timezone
from django.db import models

# Create your models here.
class HotelModel(models.Model):
    hotelName = models.CharField(max_length=100)
    hotelId = models.CharField(max_length=100)
    modelId = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    bed = models.CharField(max_length=100)
    breakfast = models.CharField(max_length=150)
    totalPrice = models.FloatField()
    amount = models.FloatField()
    commission = models.FloatField()
    price = models.FloatField()
    roomLeft = models.IntegerField()
    crawler = models.SmallIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now,  verbose_name=u'预定时间')
    update = models.DateTimeField(default=timezone.now,  verbose_name=u'更新时间')
    insertDate = models.DateTimeField(default=timezone.now,  verbose_name=u'插入时间')
    platform = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']
        db_table = "hotel"
        verbose_name = u"酒店"

class AdminUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, verbose_name=u"主键")
    username = models.CharField(max_length=50, verbose_name=u"用户名")
    password = models.CharField(max_length=50, verbose_name=u"密码")
    name = models.CharField(max_length=50, verbose_name=u"姓名")
    email = models.CharField(max_length=50, verbose_name=u"邮箱")
    status = models.CharField(max_length=10, default="1", verbose_name=u"权限")
    lastTime = models.DateTimeField(default=timezone.now,  verbose_name=u'最后操作时间')

    class Meta:
        ordering = ['id']
        db_table = "user"
        verbose_name = u"员工表"


class UserQueryHotel(models.Model):
    username = models.CharField(max_length=50, verbose_name=u"用户名")
    hotelId = models.CharField(max_length=100)
    crawler = models.SmallIntegerField(default=0)
    start = models.CharField(max_length=50, verbose_name=u"开始时间")
    end = models.CharField(max_length=50, verbose_name=u"结束时间")
    modelId = models.CharField(max_length=100)
    platform = models.CharField(max_length=100, verbose_name="平台")

    class Meta:
        ordering = ['hotelId']
        db_table = "queryhotel"
        verbose_name = u"员工监控酒店列表"
