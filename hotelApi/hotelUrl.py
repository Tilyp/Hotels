#! -*- coding: utf-8 -*-

from django.conf.urls import url

from hotelApi.views import get_hotel, login, check_user, register, crawler_all, query_all

app_name = '[student]'

urlpatterns = [
    url(r"^searchHotel", get_hotel, name="searchHotel"),
    url(r"^login", login, name="login"),
    url(r"^check_user", check_user, name="check_user"),
    url(r"^register", register, name="register"),
    url(r"^crawler_all", crawler_all, name="crawler_all"),
    url(r"^query_all", query_all, name="query_all"),
]

