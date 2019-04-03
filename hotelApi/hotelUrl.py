#! -*- coding: utf-8 -*-

from django.conf.urls import url

from hotelApi.views import get_hotel, login, check_user, register

app_name = '[student]'

urlpatterns = [
    url(r"^searchHotel", get_hotel, name="searchHotel"),
    url(r"^login", login, name="login"),
    url(r"^check_user", check_user, name="check_user"),
    url(r"^register", register, name="register"),
]