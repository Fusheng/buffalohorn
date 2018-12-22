#coding=utf-8
'''
Created on 2011-4-18
topic(非blog)形式的文章展示

@author: Fusheng
'''

from common.utils import isNumeric
from django.template import Context
from web import blogs


def topicView(request, key):
    c = Context({})
    blogs.addSessionVariables(request)
    blogs.addContextVariables(c, request)
    c['type'] = 'topic'
    command = request.GET.get('cmd')
    if command == 'reply':
        blogs.postComment(request);
    elif command == 'email':
        return blogs.emailArticleView(request)
    if isNumeric(key):
        articleModelkey = request.GET.get('key')
        return blogs.showArticleByIdView(int(key), articleModelkey, c)
    else:
        return blogs.showArticleByTagView(request, key, c['offset'], c)