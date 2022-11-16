import requests
import base58
import hmac
import hashlib
import json

key = ""
secret = ""

main_url = "https://api.inlock.io/inlock/api/v1.0"


class INLOCK_REQUEST:
    def __init__(self, endpoint, http_type, params, api_key="", api_secret=""):
        self.endpoint = endpoint
        self.http_type = http_type
        self.params = params
        self.api_key = api_key
        self.api_secret = api_secret
        self.last_request_error_msg = ""

    def reproduce_signature(self, url):
        raw_data = str(url + self.serialized_data()).encode('utf-8')
        raw_secret = base58.b58decode(self.api_secret)
        raw_check = hmac.new(raw_secret, raw_data, hashlib.sha512)
        check = base58.b58encode(raw_check.digest())
        return check.decode('utf-8')

    def serialized_data(self):
        if self.http_type == "GET":
            return ''
        # most compact format of a json, without any whitespace
        return json.dumps(self.params, indent=None, separators=(',', ':'))

    def send(self):
        self.last_request_error_msg = ""

        url = main_url + self.endpoint

        if self.http_type == "GET":
            url += "?"
            for param in self.params:
                url += param + "=" + str(self.params[param]) + "&"
            url = url[:-1]

            headers = {"X-Apikey": self.api_key,
                        "X-Signature": self.reproduce_signature(url)}

            try:
                r = requests.get(url=url, headers=headers).json()
            except Exception as e:
                print("ILK API error at sending request ", self.endpoint, "\n", e)
                return False

        if self.http_type == "POST":
            headers = {"X-Apikey": self.api_key,
                       "X-Signature": self.reproduce_signature(url)}

            try:
                r = requests.post(url=url, headers=headers, json=self.params).json()
            except Exception as e:
                print("ILK API error at sending request ", self.endpoint, "\n", e)
                return False

        if "result" in r:
            if r["result"]["status"] == "error":
                print("ILK API error at ", self.endpoint, " - ", r["error"]["message"])
                self.last_request_error_msg = r["error"]["message"]
                return False

        return r

class INLOCK_API:
    def __init__(self, api_key, api_secret):
        self.key = api_key
        self.secret = api_secret

    def getBalance(self, fiat="USD"):
        params = {"fiat": fiat}

        req = INLOCK_REQUEST("/retail/getBalance", "GET", params, self.key, self.secret)
        resp = req.send()
        return resp


inlock = INLOCK_API(key, secret)
print(inlock.getBalance())