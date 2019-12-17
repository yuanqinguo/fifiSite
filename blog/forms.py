from django import forms
from .models import ArticlePost
from .models import ArticleComments

class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        fields = ('title', 'body')

class CommentForm(forms.ModelForm):
    class Meta:
        model = ArticleComments
        fields = ("name", "email", "body", )