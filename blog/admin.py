from django.contrib import admin
from models import ArticleColumn


class ArticleColumnAdmin(admin.ModelAdmin):
    list_display = ("id", "column", "created")


admin.site.register(ArticleColumn, ArticleColumnAdmin)
