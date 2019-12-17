'''
blog urls
'''

from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^detail/(?P<article_id>\d+)/$', views.blog_detail, name="blog_detail"),
    url(r'^article_column/(?P<column_id>\d+)/$', views.blog_article_column, name='article_column'),
    url(r'^article_author/(?P<username>[-\w]+)/$', views.blog_article_author, name='article_author'),
    url(r'^article_post/$', views.article_post, name='article_post'),
    url(r'^article_del/$', views.article_delete, name='article_del'),
    url(r'^article_redit/(?P<article_id>\d+)/$', views.article_redit, name='article_redit'),
    url(r'^$', views.blog_title, name="blog_title"),
]