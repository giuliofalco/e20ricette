import django_filters
from .models import Recipe, Category, Article, Tag

class RecipeFilter(django_filters.FilterSet):
    
    subcategory = django_filters.ModelChoiceFilter(
        #queryset=Category.objects.filter(parent_category__isnull=False),
        queryset=Category.objects.none(),  # Sarà popolato dinamicamente
        label="Categoria",
        method='filter_by_subcategory'
    )
    
    descrizione_breve = django_filters.CharFilter(
        field_name='descrizione_breve',
        lookup_expr='icontains',
        label="Descrizione"
    )

    tags = django_filters.ModelChoiceFilter(
        queryset=Tag.objects.all(),
        label="Tag",
        method='filter_by_tag'
    )

    class Meta:
        model = Recipe
        fields = ['categories','description', 'tags']

    def filter_by_subcategory(self, queryset, name, value):
        if value:
            return queryset.filter(categories=value)  
        return queryset
    
    def filter_by_tag(self, queryset, name, value):
        if value:
            return queryset.filter(tags=value)
        return queryset
    
class ArticleFilter(django_filters.FilterSet):  
    content = django_filters.CharFilter(
        method='filter_content',
        label='Contenuto',
        lookup_expr='icontains',)
        
    categories = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label='Categoria',
    )

    # Aggiungi il filtro per gli articoli più recenti
    recent_articles = django_filters.ChoiceFilter(
        choices=[
            ('1',  '1 articolo più recente'),
            ('5',  '5 articoli più recenti'),
            ('10', '10 articoli più recenti'),
            ('20', '20 articoli più recenti'),
        ],
        label='Articoli più recenti',
        method='filter_recent_articles',
        required=False,
    )

    tags = django_filters.ModelChoiceFilter(
        queryset=Tag.objects.all(),
        label="Tag",
        method='filter_by_tag'
    )

    def filter_content(self, queryset, name, value):
        if value:
            return queryset.filter(content__icontains=value)
        return queryset
    
    def filter_recent_articles(self, queryset, name, value):
        if value:
            # Converte il valore da stringa a intero
            n = int(value)
            return queryset.order_by('-created_at')[:n]
        return queryset
    
    def filter_by_tag(self, queryset, name, value):
        if value:
            return queryset.filter(tags=value)
        return queryset
    class Meta:
        model = Article
        fields = ['content', 'categories','recent_articles']
