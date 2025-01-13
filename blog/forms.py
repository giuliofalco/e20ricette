from django import forms
from .models import Recipe, Article, Author, Comment
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class RecipeAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())  # Usa CKEditor per il campo description
    instructions = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Recipe
        fields = '__all__'  # Include tutti i campi del modello

class ArticleAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Article
        fields = '__all__'  # Include tutti i campi del modello

class AuthorAdminForm(forms.ModelForm):
    bio = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Author
        fields = '__all__'  # Include tutti i campi del modello



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'rate', 'content']
        widgets = {
            'rate': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'content': forms.Textarea(attrs={'rows': 4}),
        }
