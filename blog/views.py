# -*-coding:utf8-*-

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.contrib.auth.models import User
from django.http import HttpResponse,HttpResponseRedirect
from django.db.models import Count
import traceback
import redisclient
import config
import time
from markdown import markdown
from forms import ArticlePostForm, CommentForm
from models import ArticlePost, ArticleComments,ArticleColumn

#访问者的IP地址收集，分天收集
def visitor_statistics(ip):
    client = redisclient.get_redis()
    todaystr = time.strftime("%Y-%m-%d", time.localtime())
    client.sadd(str.format(config.VISITOR_DAY_TOTAL % todaystr), ip)

# redis statistics
def blog_statistics(rediskey, field):
    client = redisclient.get_redis()
    return client.hincrby(rediskey, field)

def blog_sort_statistics(rediskey, score ,blogid):
    client = redisclient.get_redis()
    client.zadd(rediskey, blogid, score)

def get_blog_statistics(rediskey, field):
    client = redisclient.get_redis()
    return client.hget(rediskey, field)

def get_blog_sort_statistics(rediskey, size):
    client = redisclient.get_redis()
    return client.zrevrange(rediskey, 0, size)

# 获取调用者IP
def getIPFromDJangoRequest(request):
    try:
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            return request.META['HTTP_X_FORWARDED_FOR']
        else:
            return request.META['REMOTE_ADDR']
    except:
        return None

#网站访问的IP量收集
def collect_client_ip(request):
    ip = getIPFromDJangoRequest(request)
    if ip and len(ip) > 0:
        visitor_statistics(ip)

# 首页视图数据
def blog_title(request):
    collect_client_ip(request)

    blogs = ArticlePost.objects.all().order_by("-created")
    paginator = Paginator(blogs, 8)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        blogs = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        blogs = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        blogs = current_page.object_list

    views = []
    if blogs and len(blogs) > 0:
        for blog in blogs:
            blog.column = ArticleColumn.objects.get(id=blog.article_column_id).column
            blog.body = markdown(blog.body)
            count = get_blog_statistics(config.BLOG_VIEWS, blog.id)
            if count == None:
                count = 0
            views.append({"id": blog.id, "views": count})

    mostids = get_blog_sort_statistics(config.BLOG_VIEWS_SORT, 10)
    mostidlist = [int(id) for id in mostids]
    mostblogs = list(ArticlePost.objects.filter(id__in=mostidlist))
    mostblogs.sort(key=lambda x: mostidlist.index(x.id))

    latest_articles = ArticlePost.objects.order_by("-created")[:5]
    most_comments = ArticlePost.objects.annotate(total_comments=Count('comments')).order_by("-total_comments")[:5]
    columns = ArticleColumn.objects.all().order_by("created")
    return render(request, "blog/titles.html", {"blogs": blogs,
                                                "most_views": mostblogs,
                                                "latest_articles": latest_articles,
                                                "most_comments": most_comments,
                                                "columns": columns,
                                                "views": views,
                                                "page": current_page})

# 博文详情页视图
def blog_detail(request, article_id):
    collect_client_ip(request)

    article = get_object_or_404(ArticlePost, id=article_id)
    #print ArticlePost.objects.get(id=article_id).updated
    article.column = ArticleColumn.objects.get(id=article.article_column_id).column
    columns = ArticleColumn.objects.all().order_by("created")

    count = blog_statistics(config.BLOG_VIEWS, article_id)
    blog_sort_statistics(config.BLOG_VIEWS_SORT, count, article_id)

    mostids = get_blog_sort_statistics(config.BLOG_VIEWS_SORT, 5)
    mostidlist = [int(id) for id in mostids]
    mostblogs = list(ArticlePost.objects.filter(id__in=mostidlist))
    mostblogs.sort(key=lambda x: mostidlist.index(x.id))

    latest_articles = ArticlePost.objects.order_by("-created")[:5]
    most_comments = ArticlePost.objects.annotate(total_comments=Count('comments')).order_by("-total_comments")[:5]

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            comment_form.save()

        #重定向到页面中的评论栏
        return HttpResponseRedirect(request.path+"#article_comment")
    else:
        comment_form = CommentForm()

    return render(request, "blog/content.html", {"article": article,
                                                 "columns": columns,
                                                 "views": count,
                                                 "most_views": mostblogs,
                                                 "latest_articles": latest_articles,
                                                 "most_comments": most_comments,
                                                 "comment_form": comment_form})


# 头部栏目查询视图
def blog_article_column(request, column_id):
    collect_client_ip(request)

    articles = ArticlePost.objects.filter(article_column=column_id).order_by("-created")
    paginator = Paginator(articles, 8)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        articles = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list

    views = []
    if articles and len(articles) > 0:
        for blog in articles:
            blog.column = ArticleColumn.objects.get(id=blog.article_column_id).column
            blog.body = markdown(blog.body)
            count = get_blog_statistics(config.BLOG_VIEWS, blog.id)
            if count == None:
                count = 0
            views.append({"id": blog.id, "views": count})

    mostids = get_blog_sort_statistics(config.BLOG_VIEWS_SORT, 5)
    mostidlist = [int(id) for id in mostids]
    mostblogs = list(ArticlePost.objects.filter(id__in=mostidlist))
    mostblogs.sort(key=lambda x: mostidlist.index(x.id))

    latest_articles = ArticlePost.objects.order_by("-created")[:5]
    most_comments = ArticlePost.objects.annotate(total_comments=Count('comments')).order_by("-total_comments")[:5]
    columns = ArticleColumn.objects.all().order_by("created")

    retObj = {}
    if articles == None:
        retObj = {"columns": columns,
                  "most_views": mostblogs}
    else:
        retObj = {"blogs": articles,
                  "most_views": mostblogs,
                  "latest_articles": latest_articles,
                  "most_comments": most_comments,
                  "columns": columns,
                  "views": views,
                  "page": current_page}

    return render(request, "blog/titles.html", retObj)

# 某用户下的所有文章视图
def blog_article_author(request, username=None):
    collect_client_ip(request)

    articles = None
    if username:
        user = User.objects.get(username=username)
        articles = ArticlePost.objects.filter(author=user).order_by("-created")
    else:
        articles = ArticlePost.objects.all().order_by("-created")

    paginator = Paginator(articles, 8)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        articles = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list

    views = []
    if articles and len(articles) > 0:
        for blog in articles:
            blog.column = ArticleColumn.objects.get(id=blog.article_column_id).column
            blog.body = markdown(blog.body)
            count = get_blog_statistics(config.BLOG_VIEWS, blog.id)
            if count == None:
                count = 0
            views.append({"id": blog.id, "views": count})

    mostids = get_blog_sort_statistics(config.BLOG_VIEWS_SORT, 5)
    mostidlist = [int(id) for id in mostids]
    mostblogs = list(ArticlePost.objects.filter(id__in=mostidlist))
    mostblogs.sort(key=lambda x: mostidlist.index(x.id))

    columns = ArticleColumn.objects.all().order_by("created")

    retObj = {}
    if articles == None:
        retObj = {"columns": columns}
    else:
        retObj = {"blogs": articles,
                  "most_views": mostblogs,
                  "columns": columns,
                  "views":views,
                  "page": current_page}

    return render(request, "blog/titles.html", retObj)

#博文新增
@login_required
@csrf_exempt
def article_post(request):
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            cd = article_post_form.cleaned_data
            try:
                new_aritcle = article_post_form.save(commit=False)
                new_aritcle.author = request.user
                new_aritcle.article_column = ArticleColumn.objects.get(id=request.POST["column_id"])
                new_aritcle.save()
                return HttpResponse("1")
            except:
                traceback.print_exc()
                return HttpResponse("2")

        else:
            return HttpResponse("3")
    else:
        article_post_form = ArticlePostForm()
        article_columns = ArticleColumn.objects.all().order_by("created")

        return render(request, "blog/article_post.html", {"article_post_form": article_post_form, "article_columns":article_columns})

#博文删除
@login_required
@require_POST
@csrf_exempt
def article_delete(request):
    try:
        article_id = request.POST["article_id"]
        article = ArticlePost.objects.get(id=article_id)
        article.delete()
        return HttpResponse("1")
    except:
        return HttpResponse("2")

#博文编辑
@login_required
@csrf_exempt
def article_redit(request, article_id):
    if request.method == "GET":
        article_columns = ArticleColumn.objects.all().order_by("created")
        article = ArticlePost.objects.get(id=article_id)
        this_article_form = ArticlePostForm(initial={"title":article.title})
        this_article_column = ArticleColumn.objects.get(id=article.article_column_id)
        return render(request, "blog/article_redit.html", {"article":article,
                                                           "article_columns": article_columns,
                                                           "this_article_column": this_article_column,
                                                           "this_article_form": this_article_form} )
    elif request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            cd = article_post_form.cleaned_data
            aritcle = ArticlePost.objects.get(id=article_id)
            try:
                aritcle.author = request.user
                aritcle.article_column = ArticleColumn.objects.get(id=request.POST["column_id"])
                aritcle.title = request.POST["title"]
                aritcle.body = request.POST["body"]
                aritcle.save()
                return HttpResponse("1")
            except:
                traceback.print_exc()
                return HttpResponse("2")

        else:
            return HttpResponse("3")

