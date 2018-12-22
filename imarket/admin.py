#coding=utf-8
'''
Created on Apr 2, 2011

@author: Fution.Bai
'''
import re

from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
import imarket.model as model
from common import decorators, utils, commonInfo
from web import blogs

@decorators.admin_login_required
def entry(request):
    type = request.GET.get('type')
    c = Context({})
    c['type'] = type
    if('tbkItems' == type):
        return tbkItems(request, c)
    if('brand' == type):
        return brand(request, c)
    if('recommandArticles' == type):
        return recommandArticles(request, c)
    if('preferences' == type):
        return preferences(request, c)
    if('tag' == type):
        return tag(request, c)
    cmd = request.GET.get('cmd')
    if('promotionMails' == cmd):
        return promotionMails(request, c)
    if('mailBodyByArticleId' == cmd):
        return mailBodyByArticleId(request, c)

def mailBodyByArticleId(request, c):
    aid = request.GET.get('article_id')
    article = blogs.getArticleById(aid)
    c['article'] = article
    t = loader.get_template('web/blogs/articleEmailTpl.html')
    response = HttpResponse(t.render(c))
    return response

def promotionMails(request, c):
    to = request.POST.get('to')
    if not to:
        t = loader.get_template('imarket/admin/promotionMails.html')
        response = HttpResponse(t.render(c))
        return response

    article_id = request.POST.get('article_id')
    if article_id:
        article = blogs.getArticleById(article_id)
        subject = article.title
        t = loader.get_template('web/blogs/articleEmailTpl.html')
        c = Context({'article':article})
        c['host'] = utils.getHost(request)
        html = t.render(c)
    addresses = re.compile('[ ,;]').split(to)
    for addr in addresses:
        if addr and len(addr):
            utils.sendMail2(sender=utils.SMTP_USER, to=addr, subject=subject, html=html)
    return commonInfo(request, "EMail发送成功")
    
def tag(request, c):
    command = request.GET.get('cmd')
    if command == 'delete':
        blogs.Tag.get(request.GET.get('key')).delete()
        return HttpResponseRedirect('/imarket/admin?type=tag')
    if  command == 'modify':
        tagModel = blogs.Tag.get(request.GET.get('key'))
        c['tag'] = tagModel
    if command == 'put':
        tag = request.POST.get('tag')
        cat = request.POST.get('cat')
        article_count = request.POST.get('article_count')
        tagModel = None
        if request.GET.get('key'):
            tagModel = blogs.Tag.get(request.GET.get('key'))
        elif request.POST.get('key'):
            tagModel = blogs.Tag.get(request.POST.get('key'))
        if not tagModel:
            tagModel = blogs.Tag(tag=tag)
        tagModel.tag=tag
        tagModel.cat=int(cat)
        tagModel.article_count=int(article_count)
        model.saveUpdateModel(tagModel)
        return HttpResponseRedirect('/imarket/admin?type=tag')
    t = loader.get_template('imarket/admin/tags.html')
    tags = model.getAllModels(blogs.Tag)
    c['tags'] = tags
    response = HttpResponse(t.render(c))
    return response

def preferences(request, c):
    command = request.GET.get('cmd')
    pref_type = request.GET.get('pref_type')
    c['pref_type']=pref_type
    if command == 'delete':
        model.Preferences.get(request.GET.get('key')).delete()
        return HttpResponseRedirect('/imarket/admin?type=preferences&pref_type='+pref_type)
    if  command == 'modify':
        preference = model.Preferences.get(request.GET.get('key'))
        c['preference'] = preference
    if command == 'put':
        if not pref_type:
            pref_type = request.POST.get('pref_type')
        pref_img_url = request.POST.get('pref_img_url')
        pref_link_url = request.POST.get('pref_link_url')
        pref_link_text = request.POST.get('pref_link_text')
        pref_link_title = request.POST.get('pref_link_title')
        preference = None
        if request.GET.get('key'):
            preference = model.Preferences.get(request.GET.get('key'))
        elif request.POST.get('key'):
            preference = model.Preferences.get(request.POST.get('key'))
        if not preference:
            preference = model.Preferences()
        preference.pref_type=pref_type
        preference.pref_img_url=pref_img_url
        preference.pref_link_url=pref_link_url
        preference.pref_link_text=pref_link_text
        preference.pref_link_title=pref_link_title
        model.saveUpdateModel(preference)
        return HttpResponseRedirect('/imarket/admin?type=preferences&pref_type='+pref_type)
    t = loader.get_template('imarket/admin/preferences.html')
    preferences = model.getAllModels(model.Preferences)
    c['preferences'] = preferences
    response = HttpResponse(t.render(c))
    return response
    
def recommandArticles(request, c):
    command = request.GET.get('cmd')
    if command == 'delete':
        blogs.RecommandArticles.get(request.GET.get('key')).delete()
        return HttpResponseRedirect('/imarket/admin?type=recommandArticles')
    if  command == 'modify':
        rmdAtls = blogs.RecommandArticles.get(request.GET.get('key'))
        c['rmdAtls'] = rmdAtls
    if command == 'put':
        article_id = request.POST.get('article_id')
        article_key = request.POST.get('article_key')
        recommand_title = request.POST.get('recommand_title')
        position = request.POST.get('position')
        rmdAtls = None
        if request.GET.get('key'):
            rmdAtls = blogs.RecommandArticles.get(request.GET.get('key'))
        elif request.POST.get('key'):
            rmdAtls = blogs.RecommandArticles.get(request.POST.get('key'))
        if not rmdAtls:
            rmdAtls = blogs.RecommandArticles(article_id=int(article_id))
        rmdAtls.article_id=int(article_id)
        rmdAtls.article_key=article_key
        rmdAtls.recommand_title=recommand_title
        rmdAtls.position=position
        model.saveUpdateModel(rmdAtls)
        if command == 'modify':
            c['rmdAtls'] = rmdAtls
        return HttpResponseRedirect('/imarket/admin?type=recommandArticles')
    t = loader.get_template('imarket/admin/recommandArticles.html')
    rmdAtlsList = model.getAllModels(blogs.RecommandArticles)
    c['rmdAtlsList'] = rmdAtlsList
    response = HttpResponse(t.render(c))
    return response


def tbkItems(request, c):
    command = request.GET.get('cmd')
    brand = request.GET.get('brand')
    if command == 'delete':
        model.TaobaokeItem.get(request.GET.get('key')).delete()
        return HttpResponseRedirect('/imarket/admin?type=tbkItems&brand='+brand)
    if command == 'put' or command == 'modify':
        num_iid = request.POST.get('num_iid')
        title = request.POST.get('title')
        pic_url = request.POST.get('pic_url')
        price = request.POST.get('price')
        click_url = request.POST.get('click_url')
        channel = request.POST.get('channel')
        taobaokeItem = None
        if request.GET.get('key'):
            taobaokeItem = model.TaobaokeItem.get(request.GET.get('key'))
        elif request.POST.get('key'):
            taobaokeItem = model.TaobaokeItem.get(request.POST.get('key'))
        if title and pic_url and click_url and channel:
            if not taobaokeItem:
                taobaokeItem = model.TaobaokeItem()
            taobaokeItem.title = title
            taobaokeItem.pic_url = pic_url
            taobaokeItem.price = price
            taobaokeItem.click_url = click_url
            taobaokeItem.channel = channel
            if num_iid:
                taobaokeItem.num_iid = long(num_iid)
            model.saveUpdateModel(taobaokeItem)
        if command == 'modify':
            c['taobaoke_item'] = taobaokeItem
    t = loader.get_template('imarket/admin/tbkAdmin.html')
    taobaoke_items = None
    if brand:
        taobaoke_items = model.getTbkItems(brand)
    else:
        taobaoke_items = model.getAllModels(model.TaobaokeItem)
    c['brand'] = brand
    c['taobaoke_items'] = taobaoke_items
    response = HttpResponse(t.render(c))
    return response

def brand(request, c):
    command = request.GET.get('cmd')
    if command == 'delete':
        model.Brand.get(request.GET.get('key')).delete()
        return HttpResponseRedirect('/imarket/admin?type=brand')
    if command == 'put' or command == 'modify':
        brand = request.POST.get('brand')
        display = request.POST.get('display')
        cid = request.POST.get('cid')
        brd = None
        if request.GET.get('key'):
            brd = model.Brand.get(request.GET.get('key'))
        elif request.POST.get('key'):
            brd = model.Brand.get(request.POST.get('key'))
        if brand and display:
            if not brd:
                brd = model.Brand()
            brd.brand = brand
            brd.display = display
            if cid:
                brd.cid = int(cid)
            model.saveUpdateModel(brd)
        if command == 'modify':
            c['brand'] = brd
    t = loader.get_template('imarket/admin/brandAdmin.html')
    brands = model.getAllModels(model.Brand)
    c['brands'] = brands
    response = HttpResponse(t.render(c))
    return response
