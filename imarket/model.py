#coding=utf-8

"""
    model.py
    Model classes and manipulations
    Copyright 2010 Fusheng
    
    @author: Fusheng baifusheng@gmail.com 
"""

from google.appengine.ext import db
from google.appengine.api import memcache
import logging

def saveUpdateModel(model):
    """
                    插入或者更新一个Model
    """
    model.put()

def getAllModels(modelClass):
    return modelClass.all()

def getIndexSlides():
    query = db.Query(Preferences)
    query.filter('pref_type =', 'INDEX_SLIDES')
    return query.fetch(limit=7, offset=0)

def getPreference(pref_type, limit=1):
    preferences = memcache.get(pref_type)
    if preferences:
        return preferences
    else:
        query = db.Query(Preferences)
        query.filter('pref_type =', pref_type)
        q = query.fetch(limit=limit, offset=0)
        if limit == 1 and len(q)==1:
            if not memcache.add(pref_type, q[0], 3600):
                logging.error("Memcache set failed.")
            return q[0]
        if not memcache.add(pref_type, q, 3600):
            logging.error("Memcache set failed.")
        return q

def getSeller(nick):
    """
                查询一个卖家
    """
    if not nick:
        return None
    seller = Seller.all().filter('nick =', nick)
    return seller

def getTUser(nick):
    if not nick:
        return None
    tUser = TUser.get_by_key_name(nick)
    return tUser 

def getAllTUser():
    return TUser.all()

def getTbkItems(brand=None):
    query = db.Query(TaobaokeItem)
    query.filter('channel =', brand)
    return query.fetch(limit=999, offset=0)
    
def getBrands(lmt=25, os=0):
    query = db.Query(Brand)
    return query.fetch(limit=lmt, offset=os)

def getSellers():
    """
                    获取所有卖家List
    """
    sellers = Seller.all()
    return sellers

def getChannelTbkItems(start, limitation, channel=None):
    query = db.Query(TaobaokeItem)
    query.filter('channel =', channel)
    results = query.fetch(limit = limitation, offset = start)
    return results

class Seller(db.Model):
    """
                    淘宝卖家
    """
    nick = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_token_secret = db.StringProperty()
    email = db.StringProperty()
    sent_t_count = db.IntegerProperty()
    
class TUser(db.Model):
    """
                    微博用户
    """
    nick = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_token_secret = db.StringProperty()
    email = db.StringProperty()
    origin = db.StringProperty() #SINAT:新浪, QQT:腾讯微博
    is_admin = db.StringProperty(default='N')#是否是管理员微博账户
    alipay_account = db.StringProperty() #支付宝账户，用来给微博用户打钱
    outer_id = db.StringProperty()#外部ID
    followers_count = db.IntegerProperty()#粉丝个数
    statuses_count = db.IntegerProperty()#微博个数
    modified_time = db.DateTimeProperty(auto_now=True)
    profile_image_url = db.StringProperty()


class TaobaokeItem(db.Model):
    """
                    淘宝客商品Item
    """
    num_iid = db.IntegerProperty()
    title = db.StringProperty()
    nick = db.StringProperty()
    pic_url = db.StringProperty()
    price = db.StringProperty()#单位：分
    click_url = db.StringProperty()
    commission = db.FloatProperty
    commission_rate = db.StringProperty()
    commission_num = db.StringProperty()
    commission_volume = db.FloatProperty
    shop_click_url = db.StringProperty()
    seller_credit_score = db.IntegerProperty()
    item_location = db.StringProperty()
    volume = db.IntegerProperty()
    taobaoke_cat_click_url = db.StringProperty()
    keyword_click_url = db.StringProperty()
    brand = db.StringProperty()#商品品牌
    cid = db.IntegerProperty()#商品分类ID
    channel= db.StringProperty()#商品所属频道
    
class Brand(db.Model):
    """
                    品牌
    """
    brand = db.StringProperty()
    display = db.StringProperty() #该品牌在页面上显示的内容
    cid = db.IntegerProperty()
    
class Preferences(db.Model):
    """
                    选项配置
    """
    pref_type = db.StringProperty()#INDEX_SLIDES主页幻灯片
    pref_img_url = db.StringProperty() 
    pref_link_url = db.StringProperty()
    pref_link_text = db.StringProperty()
    pref_link_title = db.StringProperty()