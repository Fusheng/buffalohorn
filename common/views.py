#coding=utf-8
"""

@author: Fusheng
"""

from django.http import HttpResponseRedirect
from google.appengine.api import users

from common import decorators

def login(request):
    tpe = request.GET.get('type')
    cntnue = request.GET.get('continue')
    if not cntnue:
        cntnue = '/'
    if tpe == 'sinat':
        return loginBySinaT(request, cntnue)
    return loginByGoole(request, cntnue)

@decorators.bound_t_required
def loginBySinaT(request, cntnue='/'):
    return HttpResponseRedirect(cntnue)

@decorators.google_login_required
def loginByGoole(request, cntnue='/'):
    return HttpResponseRedirect(cntnue)

def logout(request):
    cntnue = request.GET.get('continue')
    if not cntnue:
        cntnue = '/'
    logoutUrl = users.create_logout_url(cntnue)
    if 'googleAccount' in request.session:
        del request.session['googleAccount']
    if 'tUser' in request.session:
        del request.session['tUser']
    response = HttpResponseRedirect(logoutUrl)
    response.delete_cookie('nick')
    return response
