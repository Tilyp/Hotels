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
        data = {"hotelId": hotelId, "start": start, "end": end,
                "platform": platform, "username": username, "modelId": modelId}
        try:
            uqh = UserQueryHotel.objects.get(hotelId=hotelId, modelId=modelId, username=username, platform=platform)
            uqh.crawler = 0
            uqh.start = start
            uqh.end = end
            uqh.save()
        except:
            UserQueryHotel.objects.create(**data)
        update_lastTime(username=username)
        msg = {}
        return JsonResponse(msg)

def update_lastTime(username):
    user = AdminUser.objects.get(username=username)
    nowTime = datetime.datetime.now()
    user.lastTime = nowTime
    user.save()


def save_data(data):
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
                    query = UserQueryHotel.objects.get(modelId=mi["modelId"], hotelId=mi["hotelId"])
                    query.priceStatus = 1
                    query.save()
                else:
                    qhm.crawler = 0
                qhm.update = datetime.datetime.now()
                qhm.save()
        except Exception as e:
            HotelModel.objects.create(**mi)



def crawler_all(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        update_lastTime(username)
        UserQueryHotel.objects.filter(crawler=1, username=username).update(crawler=0)
    return JsonResponse({"data": {}, "status": 200})



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


def crawler(request):
    if request.method == "GET":
        update = False
        day = datetime.timedelta(days=1)
        aus = AdminUser.objects.all().values_list("username", "lastTime")
        for i in aus:
            querys = UserQueryHotel.objects.filter(username=i[0], crawler=0, priceStatus=0)
            for query in querys:
                nowTime = datetime.datetime.now()
                nextTime = (datetime.datetime.now() + day).strftime("%Y-%m-%d")
                start = query.start
                end = query.end
                nextTime = datetime.datetime.strptime(nextTime, "%Y-%m-%d")
                startTime = datetime.datetime.strptime(start, "%Y-%m-%d")
                if (nextTime - startTime).seconds > 86400:
                    start = nowTime.strftime("%Y-%m-%d")
                    end = (nowTime + day).strftime("%Y-%m-%d")
                    query.start = start
                    query.end = end
                    update = True
                lastTime = datetime.datetime.now() - i[1]
                if lastTime.seconds < 3600:
                    data = {"hotelId": query.hotelId,
                            "start": start.replace("-", "%2F"), "end": end.replace("-", "%2F"),
                            "platform": query.platform, "username": query.username, "modelId": query.modelId}
                    result = hotel.get_result(data)
                    result = save_data(result)
                else:
                    query.crawler = 1
                    update = True
                if update:
                    query.save()

    return JsonResponse({"DFS":"ASD"})


def query_all(request):
    if request.method == "POST":
        username = request.POST["username"]
        update_lastTime(username)
        result = []
        keys = ["hotelName", "hotelId", "modelId", "model", "domain", "bed", "breakfast", "price", "roomLeft", "crawler", "platform"]
        hotelList = UserQueryHotel.objects.filter(username=username).values_list("hotelId", "modelId")
        for i in hotelList:
            hm = HotelModel.objects.filter(hotelId=i[0], modelId=i[1])
            for h in hm:
                result.append({key: getattr(h, key) for key in keys})

    return {"data": result, "status": 200}

def query_model(request):
    if request.method == "POST":
        username = request.POST["username"]
        hotelId = request.POST["hotelId"]
        modelId = request.POST["modelId"]
        update_lastTime(username)
        uqh = UserQueryHotel.objects.get(hotelId=hotelId, modelId=modelId)
        uqh.priceStatus = 0
        uqh.crawler = 0
        uqh.save()
    return {"data": "", "status": 200}