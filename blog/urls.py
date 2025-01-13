from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import RecipeListView, AuthorDetailView, ArticleListView

app_name="blog"

urlpatterns = [
      path('',views.index,name="index"),
      path('ricetta/<int:id>/<str:db>',views.ricetta,name="ricetta"),
      path('ricetta_da_sola/<int:id>/<str:db>',views.ricetta_da_sola,name="ricetta_da_sola"),
      path('RecipeListView/<int:category>',RecipeListView.as_view(),name='RecipeListView'),
      path('author/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
      path('ArticleListView/<str:tag>',ArticleListView.as_view(),name='ArticleListView'),
      path('lista_commenti/<int:id_ricetta>/',views.lista_commenti,name='lista_commenti'),
      path('lista_commenti_articoli/<int:id_articolo>/',views.lista_commenti_articoli,name='lista_commenti_articoli'),
      path('add_comment/<int:recipe_id>/', views.add_comment, name='add_comment'),
      path('add_comment_articolo/<int:articolo_id>/', views.add_comment_articolo, name='add_comment_articolo'),
      path('delete_comment/<int:comment_id>/',views.delete_comment,name='delete_comment'),
      path('update_comment/<int:comment_id>/',views.update_comment,name='update_comment'),
      path('videoricette/',views.videoricette,name='videoricette'),
      path('visitor/',views.visitor,name='visitor'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)