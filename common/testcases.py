#coding=utf-8

'''
Created on Aug 2, 2010

Running appengine unit testcases locally is weird.
Always has import error, so I am using this.
@author: Fusheng
'''
from google.appengine.api import users

import common.models as models
from common import common500, common403
from django.http import HttpResponseRedirect
from django.template import Context


def entry(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect(users.create_login_url(request.get_full_path()))
    email = user.email()
    if not email or 'baifusheng@gmail.com' != email.lower():
        return common403(request, message=email);
    
    command = request.GET.get('cmd')
    c = Context({})
    c['session'] = request.session
    if command == 'initData':
        init_data(request,c)
    return common500(request)


def init_data(request,c):
    account = models.Account(account_id = models.genAccountId(),
                             email='baifusheng@gmail.com')
    account.type = 'A'
    account.put()

    sys_params = models.SysParams(param_key='TEST', value='TESTVALUE', category='TEST', description='TEST')
    sys_params.put()