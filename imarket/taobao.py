#coding=utf-8

"""
    taobao.py
    Copyright 2010 Fusheng
    
    @author: Fusheng baifusheng@gmail.com 
"""

import time
import urllib
import urllib2

import django.utils.simplejson as json
from common.utils import isNumeric, removeEmptyEntries
from django.http import HttpResponse
from django.template import Context, loader
from imarket import taobaoAPI, taobao_ke

def index(request):
    """
                    淘宝request view 入口
    """
    cmd = request.GET.get('cmd')
    c = Context({})
    c['session'] = request.session
    if cmd == 'getLatestProducts':
        return __getLatestProducts(request, c)
    elif cmd == 'showTaobaokeItems':
        return __showTaobaokeItems(request, c)
    elif cmd == 'getOneTbkItemFrm':
        tn = 'imarket/include/frmTbkItemByTag.html'
        return __showTaobaokeItems(request, c, template_name=tn, require_default_item=True)
    
def authorize(request):
    """
            未绑定淘宝卖家帐户，redirect到此
    """
    t = loader.get_template('imarket/tbAuthorize.html')
    c = Context({})
    response = HttpResponse(t.render(c))
    return response

def __showTaobaokeItems(request, c, template_name='imarket/taobaokeItems.html', require_default_item=False):
    """
        Show淘宝客推广商品
    """
    keyword = request.GET.get('keyword')
    cid = request.GET.get('cid')
    sort = request.GET.get('sort')
    start_price = request.GET.get('start_price')
    end_price = request.GET.get('end_price')
    start_credit = request.GET.get('start_credit')
    end_credit = request.GET.get('end_credit')
    area = request.GET.get('area')
    mall_item = request.GET.get('mall_item')
    overseas_item = request.GET.get('overseas_item', default='false')
    page_no = request.GET.get('page_no', default=1)
    page_size = request.GET.get('page_size', default=1)
    outer_code = determineOuterCode()
    kargs = {
            'keyword': keyword,
            'cid': cid,
            'sort':sort,
            'start_price':start_price,
            'end_price':end_price,
            'start_credit':start_credit,
            'end_credit':end_credit,
            'area':area,
            'mall_item':mall_item,
            'overseas_item':overseas_item,
            'page_no':page_no,
            'page_size':page_size,
            'outer_code':outer_code,
            }
    if not isNumeric(start_price) or not isNumeric(end_price):
        del kargs['start_price']
        del kargs['end_price']
    if isNumeric(page_no):
        page_no = int(page_no)
    else:
        page_no = 1
    t = loader.get_template(template_name)
    result = taobao_ke.getTaobaokeItems(**kargs)
    taobaokeItems = None
    total_results = 0
    if result and len(result)==2:
        taobaokeItems = result[0]
        total_results = int(result[1])
    total_page_no = 99
    if total_results % page_size == 0:
        total_page_no = total_results / page_size
    else:
        total_page_no = total_results / page_size + 1
    if require_default_item and not taobaokeItems:
        taobaokeItems = []
        taobaokeItems.append(taobao_ke.getDefaultTbkItem())
    c['taobaoke_items'] = taobaokeItems
    c['total_page_no'] = total_page_no
    c.update(removeEmptyEntries(**kargs))
    response = HttpResponse(t.render(c))
    return response

def __getLatestProducts(request, c):
    """
                    查询卖家最新上架的商品
    """
    nick = request.POST.get('nick')
    t = loader.get_template('imarket/getLatestProducts.html')
    if not nick:
        response = HttpResponse(t.render(c))
        return response
    products = doGetLatestProducts()
    c['products'] = products
    response = HttpResponse(t.render(c))
    return response
    
def doGetLatestProducts(nick=None):
    """
                    获取最新的商品
    """
    now = time.localtime()
    paramArray = {
                  'app_key':'test',
                  'fields':'product_id,name,price,pic_url,desc,created',
                  'format':taobaoAPI.FORMAT,
                  'method':'taobao.products.get',
                  'nick':'alipublic01', #TODO
                  'page_no':'1',
                  'page_size':'20',
                  'sign_method':'md5',
                  'timestamp':time.strftime('%Y-%m-%d %X', now),
                  'v':'2.0',
                  }
    sign = taobaoAPI.sign(paramArray, 'test');
    paramArray['sign'] = sign
    form_data = urllib.urlencode(paramArray)
    urlopen = urllib2.urlopen(taobaoAPI.TB_URL, form_data)
    rsp = urlopen.read()
    rsp = rsp.decode('UTF-8')
    products = json.loads(rsp)
    return products['products_get_response']['products']['product']

def doGetUser(nick=None):
    """
                    获取用户
    """
    now = time.localtime()
    paramArray = {
                  'app_key':'test',
                  'fields':'avatar',
                  'format':taobaoAPI.FORMAT,
                  'method':'taobao.user.get',
                  'nick':'alipublic01', #TODO
                  'sign_method':'md5',
                  'timestamp':time.strftime('%Y-%m-%d %X', now),
                  'v':'2.0',
                  }
    sign = taobaoAPI.sign(paramArray, 'test');
    paramArray['sign'] = sign
    form_data = urllib.urlencode(paramArray)
    urlopen = urllib2.urlopen(taobaoAPI.TB_URL, form_data)
    rsp = urlopen.read()
    rsp = rsp.decode('UTF-8')
    user = json.loads(rsp)
    return user

def determineOuterCode(is_t=False, request=None):
    if is_t and request:
        tUser = request.session['tUser']
        return 'SINAT' + tUser.screen_name
    return 'LUCKYMKT'
