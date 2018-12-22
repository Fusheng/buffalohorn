from django import http
from django.http import HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.views.generic.simple import direct_to_template

def common403(request, template_name='common/error403.html', message=None):
    t = loader.get_template(template_name)
    c = Context({})
    c['message'] = message
    return http.HttpResponseForbidden(t.render(c))

def common404(request, template_name='common/error404.html'):
    return direct_to_template(request, template=template_name)
  
def common500(request, template_name='common/error500.html'):
    return direct_to_template(request, template=template_name)

def commonInfo(request, message=None):
    template_name = 'common/info.html'
    t = loader.get_template(template_name)
    c = RequestContext(request, {'message':message})
    return http.HttpResponse(t.render(c))

def adsense(request):
    return  direct_to_template(request, template='common/adsense.html')
