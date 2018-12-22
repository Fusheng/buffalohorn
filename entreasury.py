#coding=utf-8
'''
Created on May 31, 2014

@author: FUSBAI
'''

import urllib

from google.appengine.ext import blobstore, db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from django.utils import simplejson
import datetime

class MainHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/blobstore/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
            name="submit" value="Submit"> </form></body></html>""")
        
class ListHandler(webapp.RequestHandler):
    def get(self):
        result_type = self.request.get('type')
        lastUpdatedTime = self.request.get('lastUpdatedTime')
        updDate = datetime.datetime.strptime(lastUpdatedTime, '%Y-%m-%d')
        lst = Media.gql("WHERE post_time>= :1 ORDER BY post_time DESC",updDate).fetch(10000)
        if 'json'==result_type:
            self.response.out.write(simplejson.dumps([{'name':m.name, 'url':m.url} for m in lst]))
        else:
            for m in lst:
                self.response.out.write('<p><a href="%s">%s</a></p>' \
                                        % (m.url, m.name))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        
        host_url = self.request.host_url
        media = Media(name = blob_info.filename.decode('utf-8'),
                      url = '%s/blobstore/serve/%s' % (host_url, blob_info.key()))
        media.put()
        
        self.redirect('/blobstore/serve/%s' % blob_info.key())

class UploadLinkHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/blobstore/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
            name="submit" value="Submit"> </form></body></html>""")

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)
        
class Media(db.Model):
    name = db.StringProperty()
    url = db.StringProperty()
    post_time = db.DateTimeProperty(auto_now_add=True)


app = webapp.WSGIApplication([('/blobstore/index', MainHandler),
                              ('/blobstore/list', ListHandler),
                               ('/blobstore/upload', UploadHandler),
                               ('/blobstore/uploadLink', UploadLinkHandler),
                               ('/blobstore/serve/([^/]+)?', ServeHandler)],
                              debug=True)
