#coding=utf-8
'''
Created on 2011-3-31

@author: Fusheng
'''
from django.http import HttpResponseRedirect
from google.appengine.api import users
from common import models
from common import common403

def bound_t_or_goole_login_required(handler, redirctTo='google'):
    def _wrapper(request, *args, **kw):
        tUser = request.session.get('tUser')
        user = users.get_current_user()
        if not tUser and not user:
            if redirctTo == 'sinaT':
                return HttpResponseRedirect('/imarket/authorizeSinaT')
            else:
                return HttpResponseRedirect(users.create_login_url(request.get_full_path()))
        return handler(request, *args, **kw)
    _wrapper.__name__ = handler.__name__
    return _wrapper

def bound_t_required(handler):
    """
        Decorator for views that checks that the user is bound to weibo(sina t), redirecting
        to the binding page if necessary.
    """
    def _wrapper(request, *args, **kw):
        tUser = request.session.get('tUser')
        if not tUser:
            return HttpResponseRedirect('/imarket/authorizeSinaT')
        return handler(request, *args, **kw)
    _wrapper.__name__ = handler.__name__
    return _wrapper

def admin_login_required(handler):
    """
        Decorator for views that checks that the user is logged in with google account
        and administrator privileges, redirecting
        to the login page if necessary.
    """
    def _wrapper(request, *args, **kw):
        user = users.get_current_user()
        if not user:
            return HttpResponseRedirect(users.create_login_url(request.get_full_path()))
        email = user.email()
        if not email:
            return common403(request, message=email)
        account = models.getAccountByEmail(email)
        if not account:
            return common403(request, message=email)
        type = account.type
        if isinstance(type, unicode):
            type = type.encode('utf-8')
        if 'A' == type:
            return handler(request, *args, **kw)
        return common403(request)
    _wrapper.__name__ = handler.__name__
    return _wrapper

def google_login_required(handler):
    """
        Decorator for views that checks that the user is logged in with google account,
        redirecting to the login page if necessary.
    """
    def _wrapper(request, *args, **kw):
        user = users.get_current_user()
        if not user:
            return HttpResponseRedirect(users.create_login_url(request.get_full_path()))
        email = user.email()
        request.session['googleAccount']=email
        return handler(request, *args, **kw)
    _wrapper.__name__ = handler.__name__
    return _wrapper
