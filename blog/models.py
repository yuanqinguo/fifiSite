# -*-coding:utf8-*-

from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from slugify import slugify
from django.contrib.auth.models import User


class ArticleColumn(models.Model):
    column = models.CharField(max_length=128, verbose_name='类目名')
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ("id", "column")
        verbose_name = "博客栏目"
        verbose_name_plural = "博客栏目"

    def __str__(self):
        return self.column.encode("utf8")


class ArticlePost(models.Model):
    author = models.ForeignKey(User, related_name="article", verbose_name="作者")
    title = models.CharField(max_length=300, verbose_name="标题")
    slug = models.SlugField(max_length=100)
    article_column = models.ForeignKey(ArticleColumn, related_name="article_column", verbose_name="类目名")
    body = models.TextField(verbose_name="内容")
    created = models.DateField(auto_now_add=True, verbose_name="发布时间")
    updated = models.DateField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ('title',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.title.encode("utf8")

    def save(self, *args, **kargs):
        self.slug = slugify(self.title)
        super(ArticlePost, self).save(*args, **kargs)

    def get_absolute_url(self):
        return reverse("blog:article_column", args=[self.id, self.slug])


class ArticleComments(models.Model):
    article = models.ForeignKey(ArticlePost, related_name="comments")
    name = models.CharField(max_length=90)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return "ArticleComments by {0} on {1}".format(self.name, self.article)
