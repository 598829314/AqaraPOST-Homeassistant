#!/usr/bin/env python3
import json
import sys
import time
import urllib.parse
import uuid
from base64 import b64encode

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA


print("\n #### Token Generator AqaraPost ####")
print("\n #### This is an automatic script to generate token for Node Red json HomeAssistant ####")
print(" #### for the Aqara Account, read on https://github.com/sdavides/AqaraPOST-Homeassistant ####")
print("\n")
print("#### Request info login: #### \n")

username = input("Enter your username: [example@example.com] \n")
password = input("Enter your password: [password] \n")
area = input("Enter your area: [EU],[CN],[US],[HMT],[OTHER],[AF],[RU],[AU],[ME],[KR],[JP]\n")

print("\nUsername:" + username)
print("Area:" + area)

if username == "" and len(sys.argv) > 1:
    username = sys.argv[1]
if password == "" and len(sys.argv) > 2:
    password = sys.argv[2]
if area == "" and len(sys.argv) > 3:
    area = sys.argv[3]


class PyAqara:
    areas = {
        "CN": {
            "server": "https://aiot-rpc.aqara.cn",
            "appid": "94549908487478b220992a70",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
        "EU": {
            "server": "https://rpc-ger.aqara.com",
            "appid": "7be1984f0556276133336839",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
        "RU": {
            "server": "https://rpc-ru.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "euGhPe2rcmxwculATNj45eEtnd50zp0I",
        },
        "KR": {
            "server": "https://rpc-kr.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "euGhPe2rcmxwculATNj45eEtnd50zp0I",
        },
        "JP": {
            "server": "https://rpc-kr.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "euGhPe2rcmxwculATNj45eEtnd50zp0I",
        },
        "AF": {
            "server": "https://rpc-ger.aqara.com",
            "appid": "7be1984f0556276133336839",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
        "USA": {
            "server": "https://aiot-rpc-usa.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
        "OTHER": {
            "server": "https://aiot-rpc-usa.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
        "US": {
            "server": "https://aiot-rpc-usa.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
        "HMT": {
            "server": "https://aiot-rpc-usa.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
        "AU": {
            "server": "https://rpc-au.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
        "ME": {
            "server": "https://rpc-au.aqara.com",
            "appid": "94549908487478b220992a70",
            "appkey": "Jddz01kIORDYrBzqGYgpUXKBnIHfW8E3",
        },
    }

    pubkey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCG46slB57013JJs4Vvj5cVyMpR
9b+B2F+YJU6qhBEYbiEmIdWpFPpOuBikDs2FcPS19MiWq1IrmxJtkICGurqImRUt
4lP688IWlEmqHfSxSRf2+aH0cH8VWZ2OaZn5DWSIHIPBF2kxM71q8stmoYiV0oZs
rZzBHsMuBwA4LQdxBwIDAQAB
-----END PUBLIC KEY-----"""

    def __init__(self, area_name="CN"):
        self.area = area_name
        self._userid = None
        self._token = None
        self._session = requests.session()
        self._session.headers.update(
            {
                "User-Agent": "pyAqara/1.0.0",
                "App-Version": "3.0.0",
                "Sys-Type": "1",
                "Lang": "en",
                "Phone-Model": "pyAqara",
                "PhoneId": str(uuid.uuid4()).upper(),
            }
        )

    @property
    def server(self):
        return self.areas[self.area]["server"]

    @property
    def appid(self):
        return self.areas[self.area]["appid"]

    @property
    def appkey(self):
        return self.areas[self.area]["appkey"]

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, area_name):
        normalized = area_name.upper()
        if normalized not in self.areas:
            normalized = "OTHER"
        self._area = normalized

    def encrypt_password(self, raw_password):
        rsa = PKCS1_v1_5.new(RSA.importKey(self.pubkey))
        hashed = MD5.new(raw_password.encode()).hexdigest().encode()
        return b64encode(rsa.encrypt(hashed)).decode()

    def add_headers(self, payload):
        headers = {
            "Area": self.area,
            "Appid": self.appid,
            "Appkey": self.appkey,
            "Nonce": MD5.new(str(uuid.uuid4()).encode()).hexdigest(),
            "Time": str(round(time.time() * 1000)),
            "RequestBody": payload,
        }
        if self._token is not None:
            headers["Token"] = self._token
        headers["Sign"] = self.sign_header(headers)
        del headers["Appkey"]
        del headers["RequestBody"]
        return headers

    def sign_header(self, headers):
        if headers.get("Token"):
            sign = "Appid={Appid}&Nonce={Nonce}&Time={Time}&Token={Token}&{RequestBody}&{Appkey}".format(
                **headers
            )
        else:
            sign = "Appid={Appid}&Nonce={Nonce}&Time={Time}&{RequestBody}&{Appkey}".format(
                **headers
            )
        return MD5.new(sign.encode()).hexdigest()

    def request(self, *args, **kwargs):
        method = args[0]
        if method == "GET":
            payload = urllib.parse.urlencode(kwargs["params"])
        elif method == "POST":
            if kwargs.get("json"):
                payload = json.dumps(kwargs["json"])
            elif kwargs.get("data"):
                payload = kwargs["data"]
            elif kwargs.get("params"):
                payload = urllib.parse.urlencode(kwargs["params"])
            else:
                payload = ""
        else:
            raise ValueError("Unsupported Method")
        kwargs.setdefault("headers", self.add_headers(payload))
        return self._session.request(*args, **kwargs)

    def login(self, account_name, raw_password):
        payload = {
            "account": account_name,
            "encryptType": 2,
            "password": self.encrypt_password(raw_password),
        }
        req = self.request(
            "POST",
            f"{self.server}/app/v1.0/lumi/user/login",
            json=payload,
        )
        print("#### End Request #### \n")
        response = req.json()
        if response["code"] == 0:
            self._userid = response["result"]["userId"]
            self._token = response["result"]["token"]
            print("\n #### Account info: #### \n")
            print("\nToken:" + self._token)
            print("\nServer:" + self.server.replace("https://", ""))
            print("\nAppID:" + self.appid)
            print("\nAppKey:" + self.appkey)
            print("\nUserID:" + self._userid)
            return True

        print("Login Failed!")
        print("Login Response:" + json.dumps(response, ensure_ascii=False, sort_keys=True))
        return False


aqara = PyAqara(area)

if aqara.login(username, password):
    print("\n")
    print("#### request post-login success ####")
    params = {"firmwareVersion": "3.3.2", "model": "lumi.camera.gwpagl01"}
    req = aqara.request(
        "GET",
        f"{aqara.server}/app/v1.0/lumi/ota/query/firmware/online",
        params=params,
    )
    print(json.dumps(req.json(), indent=4, sort_keys=True))
    print("\n #### END script ####")
    print("\n")
else:
    sys.exit(0)
