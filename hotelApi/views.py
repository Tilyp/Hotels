import datetime
import uuid

from django.http import JsonResponse

from crawler.hotel import Hotel
from hotelApi.models import HotelModel, AdminUser, UserQueryHotel


hotel = Hotel()


def get_hotel(request):
    if request.method == 'POST':
        hotelId = request.POST.get('hotelId')
        start = request.POST.get('start')
        end = request.POST.get('end')
        platform = request.POST.get('platform')
        username = request.POST.get('username')
        modelId = request.POST.get('model')
        today = datetime.datetime.today()
        if start == '' and end == '':
            start = today.strftime("%Y-%m-%d")
            d = datetime.timedelta(days=1)
            end = (today + d).strftime("%Y-%m-%d")
        data = {"hotelId": hotelId, "start": start.replace("-", "%2F"), "end": end.replace("-", "%2F"),
                "platform": platform, "username": username, "modelId": modelId}
        try:
            uqh = UserQueryHotel.objects.get(hotelId=hotelId, modelId=modelId, username=username, platform=platform)
            uqh.crawler = 0
            uqh.start = start
            uqh.end = end
            uqh.save()
        except:
            UserQueryHotel.objects.create(**data)
        result = hotel.get_result(data)
        result = save_data(result)
        msg = {"data": result, "status": 200}
        return JsonResponse(msg)


def save_data(data):
    result = []
    midd = {}
    for d in data:
        if d["modelId"] not in midd.keys():
            midd[d["modelId"]] = d
        else:
            if midd[d["modelId"]]["price"] > d["price"]:
                midd[d["modelId"]] = d

    for mi in midd.values():
        try:
            qhm = HotelModel.objects.get(modelId=mi["modelId"], hotelId=mi["hotelId"], breakfast=mi["breakfast"])
            if qhm:
                if qhm.price != mi["price"]:
                    qhm.price = mi["price"]
                    qhm.amount = mi["amount"]
                    qhm.commission = mi["commission"]
                    qhm.totalPrice = mi["totalPrice"]
                    qhm.crawler = 1
                    qhm.save()
                    mi["crawler"] = 1
                else:
                    mi["crawler"] = 0
        except Exception as e:
            HotelModel.objects.create(**mi)
            mi["crawler"] = 0
        result.append(mi)
    return result


def crawler_all(request):
    if request.method == 'POST':
        crawler = request.POST.get('crawler')
        HotelModel.objects.filter(crawler=1).update(crawler=crawler)

def register(request):
    if request.method == "POST":
        username = request.POST.get("userName")
        password = request.POST.get("password")
        email = request.POST.get("email")
        name = request.POST.get("name")
        status = request.POST.get("status")
        AdminUser.objects.create(
            username=username,
            password=password,
            email=email,
            status=status,
            name=name
        )
        return JsonResponse(data={"code": "0", "data": {"flag": True, "message": "success"}}, status=200)

def check_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            AdminUser.objects.get(username=username)
            message = "用户名已经存在，请重新输入！！！"
            data = False
        except Exception as e:
            message = ""
            data = True
        return JsonResponse(data={"code": "0", "data": {"flag": data,
          "username": username, "message": message}}, status=200)


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        token = str(uuid.uuid4())
        try:
            us = AdminUser.objects.get(username=username, password=password)
            request.session['token'] = token
            name = us.name
            code = "0"
            message = "登陆成功！"
        except Exception as e:
            print(e)
            code = "1"
            message = "用户名或密码错误 ！！！"
            name = ""
        return JsonResponse(data={"code": code, "data": {"name": name, "username": username,
            "message": message, "token": token}}, status=200)



def crawler():
    print("sdfsdfsadfasdff")