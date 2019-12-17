"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.http import HttpResponse

urlpatterns = [
    url(r'^robots\.txt$', lambda r: HttpResponse('User-agent: *\nDisallow: /admin\nDisallow: /login\nDisallow: /account\nDisallow: /wx', content_type='text/plain')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/', include("account.urls", namespace="account", app_name="account")),
    url(r'^blog/', include("blog.urls", namespace="blog", app_name="blog")),
    url(r'^account/', include("account.urls", namespace="account", app_name="account")),
    url(r'^wx/', include("wechat.urls", namespace="wechat", app_name="wechat")),
    url(r'^$', include("blog.urls", namespace="blog", app_name="blog")),
]
