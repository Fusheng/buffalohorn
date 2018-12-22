"""
    flickr.py
    Copyright 2004-2006 James Clarke <james@jamesclarke.info>
    Portions Copyright 2007-2008 Joshua Henderson <joshhendo@gmail.com>
    Derived from that one
    
    @author: Fution baifusheng@gmail.com 
"""

from urllib import urlopen
from xml.dom import minidom
from random import randint
import datetime

HOST = 'http://api.flickr.com'
API = '/services/rest'
API_KEY = '30657a2198ba143738882a2edc0c6e46'
USER_ID = '8127651@N07'

DEFAULT_PHOTO_URL='http://farm3.static.flickr.com/2567/3916256800_d0a6ea607a_m.jpg'
DEFAULT_PHOTO_LINK_URL='http://www.flickr.com/photos/futionbai/3916256800/'

photosData = ''

def get_random_photo_url():
    global photosData
    if not photosData or not photosData.duration \
    or (datetime.datetime.now() - photosData.duration).seconds>3600*24 :
        photosData = photos_search()
        photosData.duration = datetime.datetime.now()
    if photosData.rsp.photos.__dict__.has_key('photo'):
        if isinstance(photosData.rsp.photos.photo, list):
            length = len(photosData.rsp.photos.photo)
            if length < 1:
                return [DEFAULT_PHOTO_URL, DEFAULT_PHOTO_LINK_URL]
            photo = photosData.rsp.photos.photo[randint(1,length)]
            return [get_photo_url(photo), get_photo_webpage_url(photo)]
    pass

def get_photo_url(photo):
    farm = str(photo.farm)
    _id = str(photo.id)
    secret = str(photo.secret)
    server = str(photo.server)
    size = 'm'
    url = "http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg" % \
          (farm, server, _id, secret, size)
    return url

def get_photo_webpage_url(photo):
    url = "http://www.flickr.com/photos/%s/%s" % \
          (USER_ID, str(photo.id))
    return url

    
def photos_search():
    """Returns a list of Photo objects.
    """
    method = 'flickr.photos.search'
    min_upload_date = ''
    max_upload_date = ''
    url = '%s%s/?api_key=%s&method=%s&user_id=%s&min_upload_date=%s&max_upload_date=%s'% \
          (HOST, API, API_KEY, method, USER_ID,
                  min_upload_date, max_upload_date)
    data = _get_data(minidom.parse(urlopen(url)))
    return data

def _get_data(xml):
    """Given a bunch of XML back from Flickr, we turn it into a data structure
    we can deal with (after checking for errors)."""
    data = unmarshal(xml)
    if not data.rsp.stat == 'ok':
        msg = "ERROR [%s]: %s" % (data.rsp.err.code, data.rsp.err.msg)
        raise FlickrError, msg
    return data

class Bag: pass

class FlickrError(Exception): pass

#unmarshal taken and modified from pyamazon.py
#makes the xml easy to work with
def unmarshal(element):
    rc = Bag()
    if isinstance(element, minidom.Element):
        for key in element.attributes.keys():
            setattr(rc, key, element.attributes[key].value)
            
    childElements = [e for e in element.childNodes \
                     if isinstance(e, minidom.Element)]
    if childElements:
        for child in childElements:
            key = child.tagName
            if hasattr(rc, key):
                if type(getattr(rc, key)) <> type([]):
                    setattr(rc, key, [getattr(rc, key)])
                setattr(rc, key, getattr(rc, key) + [unmarshal(child)])
            elif isinstance(child, minidom.Element) and \
                     (child.tagName == 'Details'):
                # make the first Details element a key
                setattr(rc,key,[unmarshal(child)])
                #dbg: because otherwise 'hasattr' only tests
                #dbg: on the second occurence: if there's a
                #dbg: single return to a query, it's not a
                #dbg: list. This module should always
                #dbg: return a list of Details objects.
            else:
                setattr(rc, key, unmarshal(child))
    else:
        #jec: we'll have the main part of the element stored in .text
        #jec: will break if tag <text> is also present
        text = "".join([e.data for e in element.childNodes \
                        if isinstance(e, minidom.Text)])
        setattr(rc, 'text', text)
    return rc
