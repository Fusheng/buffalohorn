#coding=utf-8
'''
Created on 2009-XX-XX

@author: Fusheng
'''

from google.appengine.api import users
from google.appengine.ext import db

from common import decorators, utils, commonInfo, common404
from common.models import IdGen
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from imarket.model import getPreference
from web import ADMIN_EMAIL
from web.flickr import get_random_photo_url
from common.utils import check_mobile

page_size = 10

def blogsView(request):
    c = Context({})
    addSessionVariables(request)
    addContextVariables(c, request)
    
    offset = c['offset']
    command = request.GET.get('cmd')
    if not command:
        command = request.GET.get('command')
    
    if command == 'post':
        return __postArticleView(request)
    if command == 'edit':
        return __editArticleView(request)
    elif command == 'save':
        article = saveArticleService(request)
        return HttpResponseRedirect('/blogs?cmd=view&article_id=' + str(article.article_id))
    elif command == 'email':
        return emailArticleView(request)
    elif command == 'view':
        articleId = request.GET.get('article_id')
        key = request.GET.get('key')
        if articleId or key:
            return showArticleByIdView(request, articleId, key, c)
        tag = request.GET.get('tag')
        if tag and tag.strip():
            return showArticleByTagView(request, tag, offset, c)
    elif command == 'reply':
        postComment(request)
        articleId = request.GET.get('article_id')
        return HttpResponseRedirect('/blogs?command=view&article_id=' + str(articleId))
    elif command == 'getMyPhoto':
        return __getMyPhotoView(request)
    elif command == 'delete':
        return _deleteArticleView(request)
    elif command == 'deleteComment':
        return deleteCommentView(request)
    
    """
                    显示文章List
    """
    query = Article.all().order('-post_time')
    articles = query.fetch(limit=page_size, offset=offset) 
    t = loader.get_template('web/blogs/blogs.html')
    c['articles'] = articles
    return HttpResponse(t.render(c))

def addSessionVariables(request):
    """
                给session增加必要的变量
    """
    if not request.session.get('tags') or not request.session.get('techTags') \
    or not request.session.get('psnlTags'):
        tags = Tag.all().fetch(limit=500, offset=0)
        maps = {}
        ttmaps = {}
        psnlmaps = {}
        for tag in tags:
            if tag.cat>=1 and tag.cat <=99:
                maps[tag.tag] = tag.article_count
            elif tag.cat>=100 and tag.cat <=199:
                ttmaps[tag.tag] = tag.article_count
            elif tag.cat>=200 and tag.cat <=299:
                psnlmaps[tag.tag] = tag.article_count
        request.session['tags'] = maps
        request.session['techTags'] = ttmaps
        request.session['psnlTags'] = psnlmaps
        
def addContextVariables(c, request):
    """
                给Context增加必要的变量
    """
    c['session'] = request.session
    offset = request.GET.get('offset')
    if offset:
        try:
            offset = int(offset)
        except TypeError:
            offset = 0
    else:
        offset = 0
    c['offset'] = offset
    c['continue'] = utils.getAbsolutPah(request)
    pref = getPreference('taobaoHotSellIFrame')
    if pref:
        c['taobaoHotSellIFrame'] = pref.pref_link_text
    source = request.GET.get('source')
    if source:
        c['message'] = getMessageFromSource(source)

def getMessageFromSource(source):
    message = None
    if 'mail' == source:
        message = '感谢您从邮件进入本站，您是好人，会发大财的!'
    return message

@decorators.bound_t_or_goole_login_required
def postComment(request):
    cmnt = request.POST.get('comment')
    articleId = request.GET.get('article_id')
    email = request.POST.get('email').strip()
    if utils.isEmpty(cmnt) or utils.isEmpty(articleId):
        return
    cmt = Comment(comment_id=__genCommentId(),
                  article_id=int(articleId),
                  comment=cmnt,
                  email = email)
    cmt.put()
    return cmt

@decorators.admin_login_required
def __postArticleView(request):
    t = loader.get_template('web/blogs/articlePost.html')
    c = Context({})
    return HttpResponse(t.render(c))

@decorators.admin_login_required
def __editArticleView(request):
    """
                    编辑文章
    """
    key = request.GET.get('key')
    article = Article.get(key)
    if request.POST:
        ttl = request.POST.get('title')
        cnt = request.POST.get('content')
        _tag = request.POST.get('tag')
        if _tag and _tag != article.tag:
            saveUpdateTag(_tag, 1)
            saveUpdateTag(article.tag, -1)
        article.title = ttl
        article.content = cnt
        article.tag = _tag
        article.put()
        return HttpResponseRedirect('/blogs?command=view&key=' + key)
    t = loader.get_template('web/blogs/articlePost.html')
    c = Context({})
    c['article'] = article
    return HttpResponse(t.render(c))

def emailArticleView(request):
    to = request.POST.get('to')
    articleId = request.GET.get('article_id')
    article = getArticleById(articleId)
    if not to:
        t = loader.get_template('web/blogs/emailArticle.html')
        c = Context({'article':article})
        return HttpResponse(t.render(c))
    else:
        ttl = 'Your friend recommends you see this blog:' + article.title
        kargs = {}
        kargs['subject']= ttl
        kargs['to']= str(to)
        t = loader.get_template('web/blogs/articleEmailTpl.html')
        c = Context({'article':article})
        c['host'] = utils.getHost(request)
        kargs['html']= t.render(c)
        utils.sendEmail(**kargs)
        return commonInfo(request, "EMail发送成功")

def showArticleByIdView(request, aid, modelKey, c):
    article = None
    if modelKey:
        try:
            article = Article.get(modelKey)
        except Exception:
            pass
    if not article:
        article = getArticleById(aid)
    if not article:
        return common404(None)
    tag = article.tag
    similarArticles = getArticlesByTag(tag=tag, limit=6)
    if similarArticles:
        for entity in similarArticles:
            if entity.article_id == article.article_id:
                similarArticles.remove(entity)
                break
    comments = getCommentsByArticleId(aid)
    template_name = 'web/blogs/articleShow.html'
    if(check_mobile(request)):
        template_name = 'web/blogs/articleShowM.html'
    t = loader.get_template(template_name)
    c['article'] = article
    c['comments'] = comments
    c['similarArticles'] = similarArticles
    if isArticleActionPermitted(article):
        c['editable'] = 'editable'
    return HttpResponse(t.render(c))

def showArticleByTagView(request, tag, offset, c):
    articles = getArticlesByTag(tag=tag, offset=offset)
    t = loader.get_template('web/blogs/blogs.html')
    c['articles'] = articles
    c['tag'] = tag
    return HttpResponse(t.render(c))

def __getMyPhotoView(request):
    t = loader.get_template('web/blogs/myPhoto.html')
    c = Context({})
    urls = get_random_photo_url()
    c['photo_url'] = urls[0]
    c['photo_link_url'] = urls[1]
    return HttpResponse(t.render(c))

@decorators.admin_login_required
def _deleteArticleView(request):
    """
                    删除文章
    """
    articleId = request.GET.get('article_id')
    article = getArticleById(articleId)
    saveUpdateTag(article.tag, -1)
    article.delete()
    return HttpResponseRedirect('/blogs')

def deleteCommentView(request):
    """
                    删除评论
    """
    articleId = request.GET.get('article_id')
    comment_key = request.GET.get('comment_key')
    user = users.get_current_user()
    if user and user.email():
        comment = Comment.get(comment_key)
        if user.email() == comment.email:
            comment.delete()
    return HttpResponseRedirect('/blogs?cmd=view&article_id='+articleId)


def isArticleActionPermitted(article):
    user = users.get_current_user()
    if user and user.email():
        if user.email() == article.email or user.email() == ADMIN_EMAIL:
            return True
    return False

#Service methods
def getArticleById(aid):
    try:
        aid = int(aid)
    except Exception:
        return None
    article = Article.all().filter('article_id =', aid).get()
    return article

def getArticlesByTag(tag, limit=10, offset=0):
    articles = Article.all().filter('tag =', tag).order('-post_time').fetch(limit=limit, offset=offset)
    return articles

def getCommentsByArticleId(aid):
    try:
        aid = int(aid)
    except:
        return None
    comments = Comment.all().filter('article_id =', aid)
    return comments

def getRecommandArticles(position, limit=20, offset=0):
    rmdArticles = RecommandArticles.all().filter('position =', position).fetch(limit=limit, offset=offset)
    return rmdArticles

@decorators.admin_login_required
def saveArticleService(request):
    ttl = request.POST.get('title')
    cnt = request.POST.get('content')
    eml = users.get_current_user().email()
    nickname = users.get_current_user().nickname()
    _tag = request.POST.get('tag')
    _cat = request.POST.get('cat')
    aid = __genArticleId()
    article = Article(article_id=aid,
                      title=ttl,
                      content=cnt,
                      email=eml,
                      nickname=nickname,
                      reward=0,
                      tag=_tag)
    article.put()
    saveUpdateTag(_tag, 1, cat=int(_cat))
    utils.sendMail2(sender='baifusheng@gmail.com',
                    subject="You post an Article: " + ttl,
                    to=eml, body=cnt, bcc='baifusheng@gmail.com')
    return article

def saveUpdateTag(tag, countToAppend, cat=1):
    if not tag:
        return
    tag = tag.strip()
    models = Tag.all().filter('tag =', tag)
    model = None
    if models.count():
        model = models[0]
    else:
        model = Tag(tag=tag, article_count=0, cat=cat)
    count = model.article_count + countToAppend
    if count < 0:
        count = 0
    model.article_count = count
    model.put() 
        
#ID generating methods
def __genArticleId():
    q = db.GqlQuery("SELECT * FROM IdGen WHERE name = :1 ",
                    'article_id')
    result = q.fetch(1)
    if len(result) == 0:
        idGen = IdGen(name='article_id', value=1)
        idGen.put()
        return 1
    else:
        account = result[0] 
        account.value = account.value + 1
        account.put()
        return account.value
    
def __genCommentId():
    q = db.GqlQuery("SELECT * FROM IdGen WHERE name = :1 ",
                    'comment_id')
    result = q.fetch(1)
    if len(result) == 0:
        idGen = IdGen(name='comment_id', value=1)
        idGen.put()
        return 1
    else:
        account = result[0] 
        account.value = account.value + 1
        account.put()
        return account.value

class Article(db.Model):
    """
                文章表
    """
    article_id = db.IntegerProperty(required=True)
    title = db.StringProperty()
    content = db.TextProperty()
    post_time = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty(required=True)
    nickname = db.StringProperty()
    reward = db.IntegerProperty()
    tag = db.StringProperty()
    
class Comment(db.Model):
    """
                评论表
    """
    comment_id = db.IntegerProperty(required=True)
    article_id = db.IntegerProperty(required=True)
    comment = db.StringProperty(multiline=True)
    post_time = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty()#可能是Email，也可能是nick(微博用户的screen_name)
    
    def concealedEmail(self):
        """
                            隐藏部分email地址，以便显示给用户
        """
        list = str(self.email).split('@')
        if len(list) == 2:
            return list[0][:-3] + '***@' + list[1]
        if str(self.email):
            return self.email

class Tag(db.Model):
    """
                标签表
      cat:标签分类  淘宝客等推广类:1-99, 技术相关文章:100-199 个人杂记200-299
    """
    tag = db.StringProperty(required=True)
    cat = db.IntegerProperty(default=1)
    article_count = db.IntegerProperty()#该标签的文章个数

class RecommandArticles(db.Model):
    """
                推荐文章
    """
    article_id = db.IntegerProperty(required=True)
    article_key = db.StringProperty()
    recommand_title = db.StringProperty()
    position = db.StringProperty()