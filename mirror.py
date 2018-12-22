#!/usr/bin/env python
# Copyright 2008-2014 Brett Slatkin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Brett Slatkin (bslatkin@gmail.com)"

import datetime
import hashlib
import logging
import re
import time
import urllib
import wsgiref.handlers

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.runtime import apiproxy_errors

import transform_content

###############################################################################

DEBUG = False
EXPIRATION_DELTA_SECONDS = 3600

# DEBUG = True
# EXPIRATION_DELTA_SECONDS = 10

HTTP_PREFIX = "http://"

IGNORE_HEADERS = frozenset([
  "set-cookie",
  "expires",
  "cache-control",

  # Ignore hop-by-hop headers
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailers",
  "transfer-encoding",
  "upgrade",
])

TRANSFORMED_CONTENT_TYPES = frozenset([
  "text/html",
  "text/css",
])

MAX_CONTENT_SIZE = 10 ** 6 - 600

###############################################################################

def get_url_key_name(url):
  url_hash = hashlib.sha256()
  url_hash.update(url)
  return "hash_" + url_hash.hexdigest()

###############################################################################

class MirroredContent(object):
  def __init__(self, original_address,
               status, headers, data, base_url):
    self.original_address = original_address
    self.status = status
    self.headers = headers
    self.data = data
    self.base_url = base_url

  @staticmethod
  def get_by_key_name(key_name):
    return memcache.get(key_name)

  @staticmethod
  def fetch_and_store(base_url, mirrored_url):
    """Fetch and cache a page.

    Args:
      key_name: Hash to use to store the cached page.
      base_url: The hostname of the page that's being mirrored.
      translated_address: The URL of the mirrored page on this site.
      mirrored_url: The URL of the original page. Hostname should match
        the base_url.

    Returns:
      A new MirroredContent object, if the page was successfully retrieved.
      None if any errors occurred or the content could not be retrieved.
    """
    logging.debug("Fetching '%s'", mirrored_url)
    try:
      response = urlfetch.fetch(mirrored_url)
    except (urlfetch.Error, apiproxy_errors.Error):
      logging.exception("Could not fetch URL")
      return None

    adjusted_headers = {}
    for key, value in response.headers.iteritems():
      adjusted_key = key.lower()
      if adjusted_key not in IGNORE_HEADERS:
        adjusted_headers[adjusted_key] = value

    content = response.content
    page_content_type = adjusted_headers.get("content-type", "")
    for content_type in TRANSFORMED_CONTENT_TYPES:
      # startswith() because there could be a 'charset=UTF-8' in the header.
      if page_content_type.startswith(content_type):
        content = transform_content.TransformContent(base_url, mirrored_url, content)
        break

    new_content = MirroredContent(
      base_url=base_url,
      original_address=mirrored_url,
      status=response.status_code,
      headers=adjusted_headers,
      data=content)

    return new_content

###############################################################################


class BaseHandler(webapp.RequestHandler):
  def get_relative_url(self):
    slash = self.request.url.find("/", len(self.request.scheme + "://"))
    if slash == -1:
      return "/"
    return self.request.url[slash:]

  def is_recursive_request(self):
    if "AppEngine-Google" in self.request.headers.get("User-Agent", ""):
      logging.warning("Ignoring recursive request by user-agent=%r; ignoring")
      self.error(404)
      return True
    return False


class HomeHandler(BaseHandler):
  def get(self):
    if self.is_recursive_request():
      return

    # Handle the input form to redirect the user to a relative url
    form_url = self.request.get("url")
    if form_url:
      # Accept URLs that still have a leading 'http://'
      inputted_url = urllib.unquote(form_url)
      if inputted_url.startswith(HTTP_PREFIX):
        inputted_url = inputted_url[len(HTTP_PREFIX):]
      return self.redirect("/" + inputted_url)

    # Do this dictionary construction here, to decouple presentation from
    # how we store data.
    secure_url = None
    if self.request.scheme == "http":
      secure_url = "https://%s%s" % (self.request.host, self.request.path_qs)
    context = {
      "secure_url": secure_url,
    }
    self.response.out.write(template.render("templates/web/mirror.html", context))


class MirrorHandler(BaseHandler):
  def get(self):
    if self.is_recursive_request():
      return

    base_url = self.request.get('url')
    assert base_url

    # Log the user-agent and referrer, to see who is linking to us.
    logging.debug('Base_url = "%s", url = "%s"', base_url, self.request.url)

    mirrored_url = HTTP_PREFIX + base_url

    content = MirroredContent.fetch_and_store(base_url, mirrored_url)
    if content is None:
      return self.error(404)

    for key, value in content.headers.iteritems():
      self.response.headers[key] = value
    if not DEBUG:
      self.response.headers["cache-control"] = \
        "max-age=%d" % EXPIRATION_DELTA_SECONDS

    self.response.out.write(content.data)

###############################################################################

app = webapp.WSGIApplication([
  ("/mirror/", HomeHandler),
  ("/mirror/main", HomeHandler),
  ("/mirror/go", MirrorHandler),
], debug=DEBUG)