#coding=utf-8
'''
Created on 2011-4-3

@author: Fusheng
'''
from django import http
from django.utils import simplejson as json
from imarket import taobao_ke, taobao

_MIME_TYPE_AJAX = 'application/javascript'

def entry(request, method = None):
    if 'sendT' == method:
        return sendT(request)

def sendT(request):
    message = request.POST.get('message')
    image_url = request.POST.get('image_url')
    click_url = request.POST.get('click_url')
    num_iid = request.POST.get('num_iid')
    outer_code = taobao.determineOuterCode(is_t=True, request=request)
    _cu = taobao_ke.getOneTaobaokeItemClickUrl(num_iid, outer_code)
    if _cu:
        message = message + ' ' +  _cu
    else:
        message = message + ' ' + click_url

    content = json.dumps("success")
    return http.HttpResponse(content, _MIME_TYPE_AJAX)