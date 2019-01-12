#coding=utf-8
'''
Created on 2010-12-24

@author: Fusheng
'''
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from google.appengine.api.mail import send_mail
from common import commonInfo

FEEDBACK_SENT_TO_EMAIL='baifusheng@gmail.com'
ADMIN_EMAIL = 'baifusheng@gmail.com'


def feedback(request):
    email = request.POST.get('email')
    content = request.POST.get('content')
    if not content or not email or not email.index('@'):
        t = loader.get_template('web/feedback.html')
        c = Context({})
        response = HttpResponse(t.render(c))
        return response
    subject = unicode('用户的Feedback(From:%s)', 'utf-8') % email
    send_mail("baifusheng@gmail.com", FEEDBACK_SENT_TO_EMAIL, subject, content)
    return commonInfo(request, '谢谢您的反馈!')
