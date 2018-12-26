from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
)

#home,web
urlpatterns += patterns('',
 (r'^$', 'home.index'),
 (r'^index.html$', 'home.index'),
 (r'^go$', 'home.go'),
 (r'^feedback$', 'web.feedback'),
 (r'^login$', 'common.views.login'),
 (r'^logout$', 'common.views.logout'),
 (r'^test$', 'common.testcases.entry'),
 (r'^adsense.txt$', 'common.adsense'),
 (r'^salary/(?P<city_name>\w{0,50})/$', 'web.salary.salary_view'),
 (r'^calculate$', 'web.salary.calculate_view'),
 (r'^data/bankSteelDailyTransactionVolume$', 'web.data.bank_steel_daily_transaction_volume'),
 (r'^data/bankSteelDailyTransactionData$', 'web.data.bank_steel_daily_transaction_data'),
 (r'^data/job/bsdtv', 'web.data.fetch_bank_steel_data_job'),
 (r'^goog', 'web.g.g_view'),
)

#blog topic
urlpatterns += patterns('',
 (r'blogs$', 'web.blogs.blogsView'),
 (r'^topic/(?P<key>\w+)$', 'web.topic.topicView'),
)

#imarket
urlpatterns += patterns('',
 (r'imarket$', 'imarket.index.entry'),
 (r'imarket/index$', 'imarket.index.execute'),
 (r'imarket/tb$', 'imarket.taobao.index'),
 (r'imarket/authorizeSinaT$', 'imarket.sinaT.authorize'),
 (r'imarket/callback$', 'imarket.sinaT.call_back'),
 (r'imarket/t$', 'imarket.sinaT.index'),
 (r'imarket/admin$', 'imarket.admin.entry'),
 (r'imarket/ajax/(?P<method>\w+)$', 'imarket.ajax.entry'),
 (r'^channel/(?P<cat>\w+)$', 'imarket.views.channel'),
)

handler403 = 'common.common403'
handler404 = 'common.common404'
handler500 = 'common.common500'
