#coding=utf-8
'''
Created on 2011-3-31

@author: Fusheng
'''
import imarket.model as model
from django.template import Context, loader
from django.http import HttpResponse
from common.utils import isNumeric

def channel(request, cat='default'):
    """
                 商品频道
    """
    taobaoke_items = []
    if not isNumeric(cat):
        taobaoke_items = model.getChannelTbkItems(0, 63, channel=cat)
    t = loader.get_template('imarket/channel.html')
    c = Context({})
    c['session'] = request.session
    c['taobaoke_items'] = taobaoke_items
    pref = model.getPreference('taobaoHotSellIFrame')
    if pref:
        c['taobaoHotSellIFrame'] = pref.pref_link_text
    response = HttpResponse(t.render(c))
    return response