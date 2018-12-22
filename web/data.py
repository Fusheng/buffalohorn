# coding=utf-8
'''

钢银电商日成交数据

Created on 2017-03-07

@author: Fusheng
'''
import datetime
import urllib2

from google.appengine.ext import db

from django.http import HttpResponse
from django.template import Context, loader
import json


def bank_steel_daily_transaction_volume(request):
    c = Context({})
    """
       data 页面
    """
    t = loader.get_template('web/bank_steel_daily_transaction_volume.html')
    return HttpResponse(t.render(c))


def bank_steel_daily_transaction_data(request):
    """
       返回json数据
    """
    all_data = TransData.all().order('trans_date').fetch(9999)
    result = {}
    items = []
    for t in all_data:
        items.append(db.to_dict(t))
    result['list'] = items

    return HttpResponse(json.dumps(result, default=my_converter), content_type="application/json")


def my_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


url = 'https://www.banksteel.com/api/bigdata/home/v3/public/trade/deal-weight'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}


def fetch_bank_steel_data_job(request):
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    json_resp = response.read()
    data = json.loads(json_resp)
    today = data['today']
    updateTime = data['updateTime']

    trans_time = datetime.datetime.fromtimestamp(updateTime / 1000)
    trans_date = trans_time.strftime("%Y-%m-%d")

    if today == 0:
        return HttpResponse(status=201)

    q = db.GqlQuery("SELECT * FROM TransData WHERE cat = 'BSDTV' and trans_date=:1 ", trans_date)
    result = q.fetch(1)
    if len(result) == 0:
        trans_data = TransData(trans_date=trans_date, cat='BSDTV', vol=today, updated_time=datetime.datetime.now())
        trans_data.put()
        return HttpResponse(status=202)

    trans_data = result[0]
    trans_data.vol = today
    trans_data.updated_time = datetime.datetime.now()
    trans_data.put()
    return HttpResponse(status=200)


class TransData(db.Model):
    """
        交易数据表
      Cat: BSDTV 钢银日成交量数据
    """
    trans_date = db.StringProperty()  # 成交日期
    cat = db.StringProperty()  # 数据类型
    vol = db.IntegerProperty()  # 成交量
    updated_time = db.DateTimeProperty()  # 更新时间
