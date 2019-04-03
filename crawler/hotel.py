#! -*- coding:utf-8 -*-
import re
import time
import json
import datetime
import requests


class Hotel(object):


    def __init__(self):
        self.sess = requests.session()
        self.url = "https://taap.expedia.cn/Shanghai-Hotels-Cordis-Shanghai-Hongqiao.h{id}.Hotel-Information?chkin={start}&chkout={end}"
        self.cookie = ""
        self.login()

    def get_result(self, dat):
        refer = "https://taap.expedia.cn/Hotel-Search?destination=%E5%85%B0%E5%B7%9E,+%E7%94%98%E8%82%83,+%E4%B8%AD%E5%9B%BD&startDate={st}&endDate={ed}&adults=2&regionId=2071&latLong=36.32231,103.643872"
        today = datetime.datetime.today()
        d = datetime.timedelta(days=1)
        reend = (today + d).strftime("%Y/%m/%d")
        restart = today.strftime("%Y/%m/%d")
        requrl = self.url.format(id=dat["hotelId"], start=dat["start"], end=dat["end"])
        headers = {"cookie": self.cookie,
                   "referer": refer.format(st=restart, ed=reend),
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        try:
            reqs = self.sess.get(requrl, headers=headers, timeout=(30, 30))
            print("[status_code: *%d*]: %s" % (reqs.status_code, requrl))
            html = reqs.text
        except Exception as e:
            print(e)
            self.get_result(dat)
        try:
            rawDta = html.split("infosite.offersData = ")[1].split("infosite.parsedOffersData")[0].replace(";", "")
            breakFastPrice = html.split("breakfastAmountWithCurrency: ")[1].split("define('infoSitePpaModel'")[0]
            hotelname = html.split("infosite.hotelName = '")[1].split("infosite.reviewCount")[0].split("'")[0]
            breakFastPrice = re.findall("\d+", breakFastPrice)[0]
            plans = html.split("var roomsAndRatePlans = ")[1].split("return")[0].replace(";", "")
            plans = json.loads(plans)["rooms"]
            offersData = json.loads(rawDta)
            result = []
            for data in offersData["offers"]:
                item = {}
                item["totalPrice"] = data["price"]["totalPrice"]
                item["amount"] = data["totalPriceWithTaxesAndFees"]["amount"]
                try:
                    rate = data["tierInfo"]["commissionRate"]
                except Exception as e:
                    print("Check tierInfo error %s" % e)
                    flag = self.check_cookie()
                    if not flag:
                        return "login error, please check login message !"
                    self.get_result(dat)
                    continue
                item["commission"] = round(item["amount"] * rate / 100, 2)
                numberOfRoomsLeft= data["numberOfRoomsLeft"]
                if numberOfRoomsLeft == 0:
                    numberOfRoomsLeft = 999
                item["roomLeft"] = numberOfRoomsLeft
                try:
                    amenities = data["amenities"]["2205"]
                except:
                    amenities = "提供早餐(可选)-每人每晚%s元" % breakFastPrice
                roomTypeCode = data["roomTypeCode"]
                item["modelId"] = roomTypeCode
                providerId = data["inventoryProviderID"]
                room = plans["-".join([str(providerId), str(roomTypeCode)])]
                bed = room["beddingOptions"]
                if len(bed) > 1:
                    bed = "或".join(bed)
                else:
                    bed = bed[0]
                item["bed"] = bed
                item["model"] = room["name"]
                item["breakfast"] = amenities
                item["hotelName"] = hotelname
                item["hotelId"] = dat["hotelId"]
                item["price"] = round(item["amount"] - item["commission"], 2)
                item["date"] = dat["start"].replace("%2F", "-")
                item["platform"] = "expedia taap"
                item["update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result.append(item)
            return result
        except IndexError as e:
            print(e)
            return "The ID you queried does not exist"
        except Exception as e:
            print(e)
            return result

    def check_cookie(self):
        i = 0
        while True:
            if self.cookie == "":
                self.login()
            else:
                return True
            i += 1
            if i > 5:
                return False


    def login(self):
        url = "https://taap.expedia.cn/TAAP"
        loginUrl = "https://taap.expedia.cn/TAAP-Info/Login"
        data = {
            "email": "820017886@qq.com",
            "password": "Tilyp0905"
        }
        headers = {
            "cookie": 'tpid=v.1,75; currency=CNY; DUAID=7b13063d-7299-4f4e-bfd3-41c62e3e031e; MC1=GUID=7b13063d72994f4ebfd341c62e3e031e; aspp=v.1,0|||||||||||||; linfo=v.4,test|0|0|255|1|0||||||||2052|0|0||0|0|0|-1|-1; eid=351295512; AB_Test_TripAdvisor=A; _gcl_au=1.1.1162534345.1553660370; _ga=GA1.2.731718233.1553660370; rlt_marketing_code_cookie=MDP.WPK.CN.126391-75; stop_mobi=yes; CONSENTMGR=ts:1553669362693%7Cconsent:true; utag_main=v_id:0169bd5fd7fa002a0fbd21c4243403072016e06a00978$_sn:2$_ss:0$_st:1553671162961$_pn:2%3Bexp-session$ses_id:1553669251841%3Bexp-session; s_ppvl=%5B%5BB%5D%5D; s_ppv=page.TAAP.Guest.MainHome%2C34%2C34%2C603%2C462%2C603%2C1536%2C864%2C1.56%2CL',
            "origin": "https://taap.expedia.cn",
            "referer": "https://taap.expedia.cn/TAAP-Info",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }
        try:
            sess = self.sess
            sess.get(url, headers=headers, timeout=(30, 30))
            cookies = self.get_cookie(sess)
            headers["cookie"] = cookies
            reqs = sess.post(loginUrl, data=data, headers=headers, timeout=(30, 30))
            print("Login status_code [%d]" % reqs.status_code)
            self.cookie = self.get_cookie(sess)
        except Exception as e:
            self.cookie = ""
            print("Login error >> %s" % e)


    def get_cookie(self, sess):
        cookies = []
        for cookie in sess.cookies:
            cookies.append(cookie.name + "=" + cookie.value)
        return ";".join(cookies)

    def search(self):
        url ="https://taap.expedia.cn/Hotel-Search?destination=%E6%B5%A6%E4%B8%9C%2C%20%E4%B8%8A%E6%B5%B7%2C%20%E4%B8%AD%E5%9B%BD&startDate=2019/03/28&endDate=2019/03/29&regionId=&adults=2"
        headers = {
            "cookie": self.cookie,
            "referer": "https://taap.expedia.cn/Hotel-Search?destination=%E4%B8%89%E6%9E%97%E4%B8%9C%E5%9C%B0%E9%93%81%E7%AB%99&startDate=2019/04/28&endDate=2019/04/29&regionId=&adults=2",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }
        self.sess.get(url=url, headers=headers)
        jsurl = "https://taap.expedia.cn/Hotel-Search-Data?responsive=true&destination=%E6%B5%A6%E4%B8%9C%2C%20%E4%B8%8A%E6%B5%B7%2C%20%E4%B8%AD%E5%9B%BD&startDate=2019/03/29&endDate=2019/03/30&regionId=&adults=2&timezoneOffset=28800000&langid=2052&hsrIdentifier=HSR&?1552941032066"
        sdd = self.sess.post(jsurl, data={}, headers=headers)
        print(sdd)
        print(sdd.text)


if __name__ == "__main__":
    hotel = Hotel()
    # hotel.search()
    idList = ["15902552", "17835842"]
    data = {"hotelId": idList[1], "start": "2019%2F4%2F2", "end": "2019%2F4%2F4"}
    print(hotel.get_result(data))





