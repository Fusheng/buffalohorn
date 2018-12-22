#coding=utf-8
'''
Created on 2010-12-24

@author: Fusheng
'''

from common.decorators import bound_t_required
from common.utils import getCookie
from django.http import HttpResponse
from django.template import Context, loader
from imarket import model
from imarket import taobaoAPI, taobao
from web import blogs


def entry(request):
    command = request.GET.get('cmd')
    c = Context({})
    c['session'] = request.session
    if command == 'alipay':
        return alipay(request,c)
    return execute(request)

@bound_t_required
def alipay(request,c):
    alipayAccount = request.POST.get('alipayAccount')
    modelTUser = model.TUser.get_by_key_name(getCookie(request, 'nick'))
    if alipayAccount and modelTUser:
        if alipayAccount != modelTUser.alipay_account:
            modelTUser.alipay_account = alipayAccount
            modelTUser.put()
        c['alipayAccount']=alipayAccount
    elif modelTUser:
        if modelTUser.alipay_account:
            c['alipayAccount']=modelTUser.alipay_account
    t = loader.get_template('imarket/alipay_account.html')
    return HttpResponse(t.render(c))


def execute(request):
    c = Context({})
    #查询品牌
    if not request.session.get('brands'):
        entites = model.getBrands()
        brands = {}
        for brand in entites:
            brands[brand.brand]=brand.display
        request.session['brands'] = brands
    
    #查询推荐文章
    rmdArticles = blogs.getRecommandArticles(position = 'INDEX_L', limit = 20)
    c['rmdArticles'] = rmdArticles
    
    #查询主页幻灯片
    slides = model.getIndexSlides()
    c['slides'] = slides
    
    #淘宝帐户
    if request.GET.get('top_parameters'):
        topParameters = taobaoAPI.extractTopParameters(request.GET.get('top_parameters'))
        avatar = None
        if topParameters:
            tbUser = taobao.doGetUser(getCookie(request, 'nick'))
            avatar = tbUser['user_get_response']['user'].get('avatar')
            if not avatar:
                avatar = taobaoAPI.DEFAULT_AVATAR
            request.session['tbUser'] = tbUser
            request.session['avatar'] = avatar
    
    t = loader.get_template('imarket/index.html')
    c['session'] = request.session
    response = HttpResponse(t.render(c))
    return response

def __verifyTb(request):
    """
                    验证淘宝登录授权后的返回结果
    """
    top_appkey = request.GET.get('top_appkey')
    top_session = request.GET.get('top_session')
    top_parameters = request.GET.get('top_parameters')
    top_sign = request.GET.get('top_sign')
    return taobaoAPI.verify(top_appkey, top_session, top_parameters, top_sign, taobaoAPI.APP_SECRET)
    