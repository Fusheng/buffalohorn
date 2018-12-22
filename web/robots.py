#coding=utf-8
'''
Created on 2017-04-05

@author: Fusheng
'''

from google.appengine.api import users
from google.appengine.ext import db

from common import decorators, utils, commonInfo, common404
from common.models import IdGen
from django.http import HttpResponse
from django.template import Context, loader
import json



def calculate_view(request):


    data = {}


    return HttpResponse(json.dumps(data))