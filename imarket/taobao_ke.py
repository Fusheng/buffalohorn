#coding=utf-8

"""
    taobao_ke.py
    Copyright 2011 Fusheng
    
    @author: Fusheng baifusheng@gmail.com
        淘宝客模块 
"""

import django.utils.simplejson as json

import time
import urllib
import urllib2

from imarket import taobaoAPI
from imarket.model import TaobaokeItem
from common.utils import isEmpty

def getTaobaokeItems(**kargs):
    """
                    查询淘宝客推广商品
    """
    keyword = kargs.get('keyword')
    cid = kargs.get('cid')
    sort = kargs.get('sort')
    start_price = kargs.get('start_price')
    end_price = kargs.get('end_price')
    start_credit = kargs.get('start_credit')
    end_credit = kargs.get('end_credit')
    area = kargs.get('area')
    mall_item = kargs.get('mall_item')
    overseas_item = kargs.get('overseas_item')
    page_no = kargs.get('page_no')
    page_size = kargs.get('page_size')
    outer_code = kargs.get('outer_code')
    if isEmpty(keyword) and isEmpty(cid):
        return None
    
    fields = 'num_iid,title,pic_url,price,click_url,commission,commission_rate,volume'
    now = time.localtime()
    params = {'app_key':taobaoAPI.APP_KEY,
              'area':area,
              'cid':cid,
              'end_credit':end_credit,
              'end_price':end_price,
              'keyword':keyword,
              'fields':fields,
              'format':taobaoAPI.FORMAT,
              'mall_item':mall_item,
              'method':'taobao.taobaoke.items.get',
              'nick':taobaoAPI.NICK,
              'outer_code':outer_code,
              'overseas_item':overseas_item,
              'page_no':page_no,
              'page_size':page_size,
              #'pid':taobaoAPI.PID,
              'sign_method':'md5',
              'sort':sort,
              'start_credit':start_credit,
              'start_price':start_price,
              'timestamp':time.strftime('%Y-%m-%d %X', now),
              'v':taobaoAPI.V
              }
    
    if isEmpty(keyword):
        del params['keyword']
    if isEmpty(cid):
        del params['cid']
    if isEmpty(sort):
        del params['sort']
    if isEmpty(outer_code):
        del params['outer_code']
    if isEmpty(area):
        del params['area']
    if isEmpty(mall_item):
        del params['mall_item']
    if not start_price or not end_price or not start_price.strip() or not end_price.strip():
        del params['start_price']
        del params['end_price']
    elif float(start_price) > float(end_price):
        del params['start_price']
        del params['end_price']
    if not start_credit or not end_credit or not start_credit.strip() or not end_credit.strip():
        del params['start_credit']
        del params['end_credit']
    elif float(start_credit) > float(end_credit):
        del params['start_credit']
        del params['end_credit']
    
    sign = taobaoAPI.sign(params, taobaoAPI.APP_SECRET)
    params['sign'] = sign
    if isinstance(params.get('keyword'), unicode):
        params['keyword'] = params['keyword'].encode('utf-8')
    form_data = urllib.urlencode(params)
    urlopen = urllib2.urlopen(taobaoAPI.TB_URL, form_data)
    rsp = urlopen.read()
    rsp = rsp.decode('UTF-8')
    rsp = json.loads(rsp)
    taobaokeItems = convertToTaobaokeItems(rsp)
    return taobaokeItems, getTotalResults(rsp)

def getOneTaobaokeItemClickUrl(num_iid, outer_code):
    kargs = {
            'num_iids': num_iid,
            'outer_code': outer_code
            }
    tbkDtls = getOneTaobaokeItemDetail(**kargs)
    if tbkDtls:
        return tbkDtls[0].click_url 

def getOneTaobaokeItemDetail(**kargs):
    """
                    查询一个淘宝客商品, 返回click_url
    """
    outer_code = kargs.get('outer_code')
    num_iids = kargs.get('num_iids')
    if not outer_code or not num_iids:
        return None
    fields = 'click_url'
    now = time.localtime()
    params = {'app_key':taobaoAPI.APP_KEY,
              'fields':fields,
              'format':taobaoAPI.FORMAT,
              'method':'taobao.taobaoke.items.detail.get',
              'nick':taobaoAPI.NICK,
              'num_iids':num_iids,
              'outer_code':outer_code,
              'sign_method':'md5',
              'timestamp':time.strftime('%Y-%m-%d %X', now),
              'v':taobaoAPI.V
              }
    
    sign = taobaoAPI.sign(params, taobaoAPI.APP_SECRET)
    params['sign'] = sign
    if isinstance(params.get('keyword'), unicode):
        params['keyword'] = params['keyword'].encode('utf-8')
    form_data = urllib.urlencode(params)
    urlopen = urllib2.urlopen(taobaoAPI.TB_URL, form_data)
    rsp = urlopen.read()
    rsp = rsp.decode('UTF-8')
    rsp = json.loads(rsp)
    taobaokeItems = convertToTaobaokeItemDetails(rsp)
    return taobaokeItems


def getTotalResults(rsp):
    """
		搜索到符合条件的结果总数
	"""
    if not rsp or not rsp.get('taobaoke_items_get_response'):
        return 0
    return rsp.get('taobaoke_items_get_response').get('total_results', 0)

def convertToTaobaokeItems(rsp):
    if not rsp or not rsp.get('taobaoke_items_get_response'):
        return None
    if 'taobaoke_items' not in rsp.get('taobaoke_items_get_response'):
        return None
    taobaokeItems = []
    maps = rsp.get('taobaoke_items_get_response').get('taobaoke_items')
    for list in maps.values():
        for v in list:
            taobaokeItem = TaobaokeItem()
            taobaokeItem.num_iid = v.get('num_iid')
            taobaokeItem.title = v.get('title')
            taobaokeItem.pic_url = v.get('pic_url')
            taobaokeItem.click_url = v.get('click_url')
            taobaokeItem.price = float(v.get('price'))
            taobaokeItem.item_location = v.get('item_location')
            taobaokeItems.append(taobaokeItem)
    return taobaokeItems

def convertToTaobaokeItemDetails(rsp):
    if not rsp or not rsp.get('taobaoke_items_detail_get_response'):
        return None
    if 'taobaoke_item_details' not in rsp.get('taobaoke_items_detail_get_response'):
        return None
    taobaokeItems = []
    maps = rsp.get('taobaoke_items_detail_get_response').get('taobaoke_item_details')
    for list in maps.values():
        for v in list:
            taobaokeItem = TaobaokeItem()
            taobaokeItem.click_url = v.get('click_url')
            taobaokeItems.append(taobaokeItem)
    return taobaokeItems

def getDefaultTbkItem():
    taobaokeItem = TaobaokeItem()
    taobaokeItem.pic_url = 'https://img.alicdn.com/bao/uploaded/i3/TB11D0MPVXXXXcuXVXXXXXXXXXX_!!0-item_pic.jpg_430x430q90.jpg'
    taobaokeItem.click_url = 'https://s.click.taobao.com/2r5ZB2x?&scm=20140618.1.02030002.201612271329s12'
    return taobaokeItem

class TaobaoKeError(Exception):
    """
                淘宝客 Error
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#TODO Delete them after testing
tbk_test_data = """
{
    "taobaoke_items_get_response": {
        "taobaoke_items": {
            "taobaoke_item": [{
                "num_iid": 4891397896,
                "title": "七匹狼 简约造型男士针扣牛皮皮带 PLH792036400 专柜正品",
                "pic_url": "http://img05.taobaocdn.com/bao/uploaded/i5/T13sVfXftBXXa_EcIY_025652.jpg_sum.jpg",
                "price": "115.00",
                "click_url": "http://s.click.taobao.com/t_1?i=rEC7RT4gvPZoJQ%3D%3D&p=mm_10011550_0_0&n=11",
                "commission": "1.73",
                "commission_rate": "1.5%",
                "commission_volume": "0",
                "item_location": "杭州",
                "volume": 100
                },
                {
                "num_iid": 4891397897,
                "title": "七匹狼 简约造型男士针扣牛皮皮带 PLH792036400 专柜正品",
                "pic_url": "http://img05.taobaocdn.com/bao/uploaded/i5/T13sVfXftBXXa_EcIY_025652.jpg_sum.jpg",
                "price": "115.00",
                "click_url": "http://s.click.taobao.com/t_1?i=rEC7RT4gvPZoJQ%3D%3D&p=mm_10011550_0_0&n=11",
                "commission": "1.73",
                "commission_rate": "1.5%",
                "commission_volume": "0",
                "item_location": "杭州",
                "volume": 100
                }]
        },
        "total_results": 2
    }
}
"""

one_tbk_detail_test_data="""
{
 "taobaoke_items_detail_get_response": {
  "total_results": 1,
        "taobaoke_item_details": {
            "taobaoke_item_detail": [{
                "click_url": "http://taobao.xxx.com",
                "shop_click_url": "http://easesou.taobao.com",
                "seller_credit_score": 90
            }]
        }
    }
}
"""