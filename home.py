from django.http import HttpResponseRedirect

from web.utils import getUrl

def index(request):
    #Go to imarket index page.
    return HttpResponseRedirect('/blogs')

def go(request):
    linkId = request.GET.get('link_id')
    url = getUrl(int(linkId))
    return HttpResponseRedirect(url)