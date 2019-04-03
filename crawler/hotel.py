#! -*- coding:utf-8 -*-
import re
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
            "cookie": "tpid=v.1,75; currency=CNY; DUAID=7b13063d-7299-4f4e-bfd3-41c62e3e031e; MC1=GUID=7b13063d72994f4ebfd341c62e3e031e; aspp=v.1,0|||||||||||||; eid=351295512; AB_Test_TripAdvisor=A; _gcl_au=1.1.1162534345.1553660370; _ga=GA1.2.731718233.1553660370; stop_mobi=yes; rlt_marketing_code_cookie=; _cls_v=eeb9d9ed-b405-41c0-8763-7ca135648f07; ndcd=wc1.1.w-681606.1.2.SZQpY1jJxVs9negLfYeleg%2C%2C.K5rS7imgZKiwsJDgB96tve1ktZ5qY1Xx4uxkV-_EfBC3HuLt3p59pWoxME0Iu_Z9ahk1D5oXvqM-EcpW3fTg2cC-9wOblAHBFyLLK6TzVLtFbifxspbth0NwA98kxGqA4c7QthN5d8R6icModyxoT9DjAcKq73dZGs9BvZtHAuE%2C; utag_main=v_id:0169bd5fd7fa002a0fbd21c4243403072016e06a00978$_sn:6$_ss:0$_st:1553878990164$_pn:2%3Bexp-session$ses_id:1553877155605%3Bexp-session; HMS=70a5764f-de28-4c49-9644-245ae0aadfdc; ak_bmsc=30DCA4BAAB1E6E0F614B7190276A9F8E1B948C16351F0000BCC6A45C09F47C69~plyBVkfqulUSiz+RPGryXaE2HW2LoTsMlxBOT9FzfSqJ4nprjLWVyE4qaXy6nQoI6ZN2JCxrOG9jnDd2sZoC9f9XmPZJ/ZQbYi99R7jz2U3h9wcUGrm6oCuHrlbrpj3o3tDIKybhHYxkjwI1MfGOO3aVdB9aoJotDToLT/3VeAQRAPQz0UCogGrwgprcLxWN5aiwB4oZNtugRr/QzIRfn4qVtQ8lZM/PGHdNzzCuvOMWg=; JSESSION=c213138f-e7f4-4010-b14e-a619dce92474; AMCVS_C00802BE5330A8350A490D4C%40AdobeOrg=1; s_cc=true; _cls_s=53452b7a-69e8-44e4-acb6-b10631a944da:1; iEAPID=126391; x-CGP-exp-24700=1; x-CGP-exp-24699=1; x-CGP-exp-28604=1; linfo=v.4,Guest|0|0|255|1|0||||||||2052|0|0||0|0|0|-1|-1; JSESSIONID=8265D306BA91C93C5B94BF80A4C85676; AWSELB=D79B53F10ADCF9DDDF09C7B84896C09A6222EC2F5D7767E9135D856FC4ED805E4F688FFB95F2A58F84B43F61ADD9D865003C2FA4F6DB19396FE1D59B863EAEE875DC3EE916; csrfTokenL=fece3b7b-2a8c-41f6-908a-ef981befe3d0|kGowj__s_RqrGCTlRg5fNjisYc3lSDPitKjD0LplDSFQz43LFd-M18Gj8HPASiZqtQwFwVxtS_R_r6fKOFW4KQ; CONSENTMGR=ts:1554303578968%7Cconsent:true; AMCV_C00802BE5330A8350A490D4C%40AdobeOrg=-179204249%7CMCIDTS%7C17990%7CMCMID%7C83625257191847217733763001157949062544%7CMCAAMLH-1554908379%7C11%7CMCAAMB-1554908379%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1554310779s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C2.5.0; cesc=%7B%22dps%22%3A%5B%22MDP.WPK.CN.126391-75%22%2C1554134006563%5D%2C%22entryPage%22%3A%5B%22page.TAAP.Guest.MainHome%22%2C1554303632793%5D%2C%22rlt%22%3A%5B%22MDP.WPK.CN.126391-75%22%2C1554134006567%5D%2C%22cid%22%3A%5B%22MDP.WPK.CN.126391-75%22%2C1554134006567%5D%7D; s_ppn=page.TAAP.TravelAgent.MainHome; s_ppvl=Homepage%2C100%2C100%2C603%2C1229%2C603%2C1536%2C864%2C1.56%2CP; s_ppv=page.Account.SignIn%2C52%2C52%2C603%2C621%2C603%2C1536%2C864%2C1.56%2CP",
            "origin": "https://taap.expedia.cn",
            "referer": "https://taap.expedia.cn/TAAP-Info",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }
        try:
            sess = self.sess
            # sess.get(url, headers=headers, timeout=(30, 30))
            # cookies = self.get_cookie(sess)
            # headers["cookie"] = cookies
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





