#coding=utf-8

"""
    taobaoAPI.py
          淘宝Open API相关的调用处理
    Copyright 2010 Fusheng
    
    @author: Fusheng baifusheng@gmail.com 
"""
import hashlib
import base64
import md5

"""
        淘宝Configuration
"""
TB_URL_TEST = 'http://gw.api.tbsandbox.com/router/rest'
TB_URL = 'http://gw.api.taobao.com/router/rest'
APP_KEY = '12180748'
APP_KEY_TEST = 'test'
APP_SECRET = 'a05d3d37a54c02ff3195e06b829cae24'
APP_SECRET_TEST = 'test'
FORMAT = 'json'
V='2.0'#Version
DEFAULT_AVATAR = 'http://a.tbcdn.cn/app/sns/img/default/avatar-120.png'
PID = 'mm_10157600_0_0' #淘宝客PID:
NICK = 'xuntion'

def sign(param, sercetCode):
    """
                   签名函数
    """
    src = sercetCode + ''.join(["%s%s" % (k, v) for k, v in sorted(param.items())]) + sercetCode
    src= src.encode('utf-8')
    return md5.new(src).hexdigest().upper()

def verify(top_appkey, top_session, top_parameters, top_sign, app_secret):
    """
                    验证签名是否合法
    """
    if not (top_appkey and top_session and top_parameters and top_sign and app_secret):
        return False
    m = hashlib.md5(top_appkey + top_parameters + top_session + app_secret)
    computedTopSign = base64.b64encode(m.digest().hexdigest())
    if top_sign != computedTopSign:
        return False
    return True

def extractTopParameters(topParameters):
    if not topParameters:
        return
    params = {}
    s  = base64.decodestring(topParameters)
    list = s.split('&')
    for pair in list:
        p = pair.split('=')
        if len(p) != 2:
            continue
        else:
            params[p[0]] = p[1]
    return params

class TaobaoError(Exception):
    """Taobao OPEN Exception"""

    def __init__(self, reason):
        self.reason = reason#.encode('utf-8')

    def __str__(self):
        return self.reason