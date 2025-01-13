from django.contrib import admin
from .models import *
from .forms import RecipeAdminForm, ArticleAdminForm, AuthorAdminForm # Importa il tuo form personalizzato

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category','ordine')
    search_fields = ('name',)
    list_filter = ('parent_category',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    form = AuthorAdminForm
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title','author', 'created_at', 'updated_at',)
    search_fields = ('title', 'author__user__username',)
    list_filter = ('categories', 'tags', 'created_at', 'updated_at')
    filter_horizontal = ('categories', 'tags')

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

class ImmaginiInline(admin.TabularInline):
    model = Immagini
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm  # Usa il form personalizzato
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'author__user__username',)
    list_filter = ('categories', 'tags', 'created_at', 'updated_at')
    filter_horizontal = ('categories', 'tags')
    inlines = [RecipeIngredientInline, ImmaginiInline ]
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'article', 'recipe')
    search_fields = ('author__username', 'content',)
    list_filter = ('created_at',)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('titolo','autore', 'data', 'visibile',)
    search_fields = ('title', 'author',)
    list_filter = ('data',)


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address','visit_count','last_visit','city','country','region')