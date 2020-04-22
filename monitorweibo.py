import requests
import time
import json


class monitorweibo:

    def __init__(self):
        self.idlist = []
        self.returnDic = {}
        self.session = requests.session()
        self.headers = {
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Length': '262',
            'Host': 'passport.weibo.cn',
            'Origin': 'https://passport.weibo.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

    def login(self, username, password):
        """
        登录微博
        :param username: 用户名
        :param password: 密码
        :return:
        """
        loginapi= 'https://passport.weibo.cn/sso/login'
        data = {
            'username': username,
            'password': password,
            'savestate': 1,
            'r': 'https://m.weibo.cn/',
            'ec': 0,
            'pagerefer': 'https://m.weibo.cn/login?backURL=https%253A%252F%252Fm.weibo.cn%252F',
            'entry': 'mweibo',
            'wentry': '',
            'loginfrom': '',
            'client_id': '',
            'code': '',
            'qq': '',
            'mainpageflag': 1,
            'hff': '',
            'hfp': '',
        }

        try:
            r = self.session.post(loginapi, data=data, headers=self.headers)
            if r.status_code == 200 and json.loads(r.text)['retcode'] == 20000000:
                print("登录成功")
                msg = {
                    'code': 200,
                    'message': '登录成功'
                }
                return msg
            else:
                msg = {
                    "code": 403,
                    "message": "登录失败"
                }
                return msg

        except Exception as e:

            print("登录接口异常")

    def getconId(self, uid):
        """
        获取微博数据
        :param uid: 相关人员id
        :return:
        """
        userinfoapi = 'https://m.weibo.cn/api/container/getIndex'
        param = {
            'uid': uid,
            't': '0',
            'luicode': '10000011',
            'lfid': '100103type=1',
            'type': 'uid',
            'value': uid,
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'mweibo-pwa': '1',
            'pragma': 'no-cache',
            'referer': '',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.headers['User-Agent'],
            'x-requested-with': 'XMLHttpRequest',
            'upgrade-insecure-requests': '1',
        }
        res = self.session.get(userinfoapi, params=param, headers=headers)
        for i in res.json()['data']['tabsInfo']['tabs']:
            # print(i['tabKey'])
            if i['tabKey'] == 'weibo':
                conId = i['containerid']
        param['containerid'] = conId
        items = []
        resq = self.session.get(userinfoapi, params=param, headers=headers)
        for i in resq.json()['data']['cards']:
            if i['card_type'] == 9:
                items.append(i['mblog']['id'])
        return items

    def newweibo(self, uid, diffid):
        """
        获取更新微博的内容
        :param uid:
        :param diffid:
        :return:
        """
        userinfoapi = 'https://m.weibo.cn/api/container/getIndex'
        param = {
            'uid': uid,
            't': '0',
            'luicode': '10000011',
            'lfid': '100103type=1',
            'type': 'uid',
            'value': uid,
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'mweibo-pwa': '1',
            'pragma': 'no-cache',
            'referer': '',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.headers['User-Agent'],
            'x-requested-with': 'XMLHttpRequest',
            'upgrade-insecure-requests': '1',
        }
        res = self.session.get(userinfoapi, params=param, headers=headers)
        for i in res.json()['data']['tabsInfo']['tabs']:
            # print(i['tabKey'])
            if i['tabKey'] == 'weibo':
                conId = i['containerid']
        param['containerid'] = conId
        resq = self.session.get(userinfoapi, params=param, headers=headers)
        for i in resq.json()['data']['cards']:
            if i['card_type'] == 9:
                if i['mblog']['id'] == diffid:
                    self.returnDic['created_at'] = i['mblog']['created_at']
                    self.returnDic['returnDic'] = i['mblog']['source']
                    self.returnDic['text'] = i['mblog']['text']
                    self.returnDic['nickName'] = i['mblog']['user']['screen_name']
                    if 'pics' in i['mblog']:
                        for j in i['mblog']['pics']:
                            self.returnDic['picUrls'] = []
                            self.returnDic['picUrls'].append(j['url'])

    def createping(self, weiboid, message):
        """
        创建评论
        :param weiboid:
        :param message:
        :return:
        """
        configurl = 'https://m.weibo.cn/api/config'
        tokenr = self.session.get(configurl)
        # print(tokenr.json()['data']['st'])
        create = 'https://m.weibo.cn/api/comments/create'
        data = {
            'content': message,
            'mid': weiboid,
            'st': tokenr.json()['data']['st'],
            '_spr': 'screen:1680x1050'
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9', 'cache-control': 'no-cache', 'content-length': '81',
            'mweibo-pwa': '1', 'origin': 'https://m.weibo.cn', 'pragma': 'no-cache',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'x-requested-with': 'XMLHttpRequest',
            'user-agent': self.headers["User-Agent"], 'x-xsrf-token': tokenr.json()['data']['st']}
        # print(headers['x-xsrf-token'])
        result = self.session.post(create, data=data, headers=headers)
        # print(result.status_code)
        # print(result.text)
        if result.json()['ok'] == 1 and result.status_code == 200:
            print("-----评论成功-----")
        else:
            print("---评论失败---")


a = monitorweibo()
username = input("请输入微博账户名：")
password = input("请输入微博密码：")
if a.login(username,password)['code'] != "403":
    uuid = int(input("请选择：1、周深；2、木小容；3.熊小燕 :"))
    if uuid == 1:
        uid = 1736988591
    elif uuid == 2:
        uid = 2379178285

    elif uuid == 3:
        uid = 3735319521
    pinglun = input("请输入评论的内容:")

    n = 0
    while 1:
        time.sleep(5)
        items = []
        difflist = []
        n = n+1
        print('----------循环第%s次-------' %n)
        if n == 1:
            a.idlist = a.getconId(uid)

        else:
            items = a.getconId(uid)
            if set(items) <= set(a.idlist):
                print("没有更新")
            else:
                print(" 有更新")
                for i in items:
                    if i not in a.idlist:
                        difflist.append(i)

                for j in difflist:
                    a.createping(j, pinglun)
                    a.idlist.append(j)
                    a.newweibo(uid, j)
                    print('-----更新内容------')
                    print(a.returnDic)


else:
    print("登录失败请重新启动")








