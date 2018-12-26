#!/usr/bin/python
# -*- coding: utf-8 -*-
#


import urllib2
import socket
import time
import gzip
import StringIO
import re
import random
import types
from bs4 import BeautifulSoup
from google.appengine.api import urlfetch

from django.http import HttpResponse


class SearchResult:
    def __init__(self):
        self.url = ''
        self.title = ''
        self.content = ''

    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = content

    def printIt(self, prefix=''):
        print 'url\t->', self.url
        print 'title\t->', self.title
        print 'content\t->', self.content
        print

    def writeFile(self, filename):
        file = open(filename, 'a')
        try:
            file.write('url:' + self.url + '\n')
            file.write('title:' + self.title + '\n')
            file.write('content:' + self.content + '\n\n')
        except IOError, e:
            print 'file error:', e
        finally:
            file.close()


class GoogleAPI:
    def __init__(self):
        timeout = 40
        socket.setdefaulttimeout(timeout)

    def randomSleep(self):
        sleeptime = random.randint(60, 120)
        time.sleep(sleeptime)

    def extractDomain(self, url):
        """Return string
        extract the domain of a url
        """
        domain = ''
        pattern = re.compile(r'http[s]?://([^/]+)/', re.U | re.M)
        url_match = pattern.search(url)
        if(url_match and url_match.lastindex > 0):
            domain = url_match.group(1)

        return domain

    def extractUrl(self, href):
        """ Return a string
        extract a url from a link
        """
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)&', re.U | re.M)
        url_match = pattern.search(href)
        if(url_match and url_match.lastindex > 0):
            url = url_match.group(1)

        return url

    def extractSearchResults(self, html):
        """Return a list
        extract serach results list from downloaded html file
        """
        results = list()
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', id='search')
        if (type(div) != types.NoneType):
            lis = div.findAll('div', {'class': 'g'})
            if(len(lis) > 0):
                for li in lis:
                    result = SearchResult()
                    h3 = li.find('h3', {'class': 'r'})
                    if(type(h3) == types.NoneType):
                        continue
                    # extract domain and title from h3 object
                    link = h3.find('a')
                    if (type(link) == types.NoneType):
                        continue
                    url = link['href']
                    url = self.extractUrl(url)
                    if(cmp(url, '') == 0):
                        continue
                    title = link.renderContents()
                    title = re.sub(r'<.+?>', '', title)
                    result.setURL(url)
                    result.setTitle(title)
                    span = li.find('span', {'class': 'st'})
                    if (type(span) != types.NoneType):
                        content = span.renderContents()
                        content = re.sub(r'<.+?>', '', content)
                        result.setContent(content)
                    results.append(result)
        return results

    def search(self, query, lang='en', num=10):
        """Return a list of lists
        search web
        @param query -> query key words
        @param lang -> language of search results
        @param num -> number of search results to return
        """
        search_results = list()
        query = urllib2.quote(query)

        for p in range(0, pages):
            start = p * 10
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (base_url, lang, 10, start, query)
            try:
                request = urllib2.Request(url)
                request.add_header('User-agent', user_agent)
                request.add_header('connection', 'keep-alive')
                request.add_header('Accept-Encoding', 'gzip')
                request.add_header('referer', base_url)
                response = urlfetch.fetch(url, validate_certificate=True)
                if response.status_code == 200:
                    html = response.content
                    results = self.extractSearchResults(html)
                    search_results.extend(results)
            except urllib2.URLError, e:
                print 'url error:', e
            except Exception, e:
                print 'error:', e
        return search_results


def crawler(keyword):

    # Create a GoogleAPI instance
    api = GoogleAPI()

    # set expect search results to be crawled
    expect_num = 10
    results = api.search(query=keyword, num=expect_num)
    return results


pages = 1
base_url = "https://www.google.com"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'


def g_view(request):
    keyword = request.GET.get('q')
    result = crawler(keyword)
    return HttpResponse(result)
