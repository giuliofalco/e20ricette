from blog.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django_filters.views import FilterView
from .filters import RecipeFilter, ArticleFilter
from django.views.generic import DetailView, ListView
from .forms import CommentForm
import uuid
from django.db.models import Count

def index(request):
  # home page
    video = Video.objects.filter(visibile=True)[:2]
    # se non ne trovi prendi quelli di farfalla
    if len(video) < 2:
        video = Video.objects.using('farfalla').filter(visibile=True)[:3]
    ricette = Recipe.objects.all().prefetch_related('immagini_set')[:5]
    ricette_farfalla = Recipe.objects.using('farfalla').all().prefetch_related('immagini_set')[:5]
    categorie = Category.objects.filter(parent_category__isnull = True)
    slideshow = Recipe.objects.filter(slideshow=True)
    titoli = [slide.title for slide in slideshow]
    autore = Author.objects.get(id=1) # l'autrice 

    visitor_ip = request.META.get('REMOTE_ADDR')  # Indirizzo IP del visitatore
    visitor, created = Visitor.objects.get_or_create(ip_address=visitor_ip)

    if created:
        visitor.visit_count = 1  # Nuovo visitatore unico
    else:
        visitor.visit_count += 1  # Incrementa il numero di visite per questo visitatore
        visitor.save()
    
    visitor.update_location()
    context = {'video':video, 'ricette': ricette, 'categorie':categorie, 
               'slideshow': slideshow, 'titoli':titoli, 'autore':autore,
               'ricette_farfalla':ricette_farfalla}
    return render(request,"blog/index.html",context)

def ricetta(request,id,db):
  # apre il template omonimo che mostra tutti i dettagli di una specifica ricetta
   
    if db == 'farfalla':
      recipe = Recipe.objects.using('farfalla').get(id=id)
      db = 'farfalla'
    else:
      recipe = Recipe.objects.get(id=id)
      db = ''
    comment_count = recipe.comment_set.count() # Conta il numero di commenti associati alla ricetta
     
    # Recupera gli ingredienti con quantità e unità attraverso la relazione RecipeIngredient
    ingredients = RecipeIngredient.objects.filter(recipe=recipe).select_related('ingredient')
    context = {'recipe':recipe, 'db':db, 'comment_count' : comment_count,
               'ingredients': ingredients,  # Elenco ingredienti con dettagli }
            }
    return render(request,"blog/ricetta.html",context)

def ricetta_da_sola(request,id,db):
  # mostra la ricetta in una finestra individuale per possibile stampa su file
  # apre il template omonimo che mostra tutti i dettagli di una specifica ricetta
    if db == 'farfalla':
       recipe = Recipe.objects.using('farfalla').get(id=id)
       ingredients = RecipeIngredient.objects.using('farfalla').filter(recipe=recipe).select_related('ingredient')
       db = 'farfalla'
    else:
       recipe = Recipe.objects.get(id=id)
       # Recupera gli ingredienti con quantità e unità attraverso la relazione RecipeIngredient
       ingredients = RecipeIngredient.objects.filter(recipe=recipe).select_related('ingredient')
       db = ''
    context = {
            'recipe':recipe,
            'ingredients': ingredients,  # Elenco ingredienti con dettagli
            'db':db,
            }
    return render(request,"blog/ricetta_da_sola.html",context)

class RecipeListView(FilterView):
    # vista per elenco ricette. Parametrica rispetto alla categoria principale (category)

    model = Recipe
    template_name = 'blog/elenco_ricette.html'
    filterset_class = RecipeFilter
    context_object_name = 'recipes'

    def get_queryset(self):
        # Recupera la categoria passata come parametro
        id = self.kwargs.get('category')  # 'category' corrisponde al nome nel path
        print(f"Categoria ID ricevuto: {id}")
        self.category = get_object_or_404(Category, id=id)

        # Filtra le ricette solo per la categoria specificata
        return Recipe.objects.filter(categories=self.category).annotate(comment_count=Count('comment'))

    def get_filterset(self, filterset_class):
        # Recupera il filtro e lo popola con le sottocategorie della categoria passata
        filterset = super().get_filterset(filterset_class)
        if hasattr(self, 'category'):
            filterset.form.fields['subcategory'].queryset = Category.objects.filter(parent_category=self.category)
        return filterset

    def get_context_data(self, **kwargs):
        # Passa la categoria selezionata al template
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class AuthorDetailView(DetailView):
    # vista per le informazioni sull'autore
    model = Author
    template_name = 'blog/author_detail.html'
    context_object_name = 'author'

class ArticleListView(FilterView):
    # vista per l'elenco degli articoli, parametro tag per il tipo di articolo 'cuciniamo' o 'scorribande'
    model = Article
    filterset_class = ArticleFilter
    template_name = 'blog/article_list.html'
    paginate_by = 10
    
    def get_queryset(self):
        # Filtra gli articoli che hanno il tag 'scorribande'
        tag = self.kwargs.get('tag')  # parametro per il tipo di articolo ('scrribande' o 'cuciniamo')
        if tag:
           return Article.objects.filter(tags__name=tag).distinct().annotate(comment_count=Count('comment'))
        else:
           return Article.objects.all()
    
    def get_context_data(self, **kwargs):
       
        context = super().get_context_data(**kwargs)
        tag = self.kwargs.get('tag')  # parametro per il tipo di articolo ('scorribande' o 'cuciniamo')
        if tag == 'scorribande':
            titolo = 'Le mie scorribande'
        elif tag == 'cuciniamo':
            titolo = 'Cuciniamo insieme'
        else:
            titolo = 'Cuciniamo insieme'
        context['title'] = titolo
        return context
    
def lista_commenti(request,id_ricetta):
    # elenca i commenti associati ad una specifica ricetta

    ricetta = Recipe.objects.get(id=id_ricetta)
    commenti = Comment.objects.filter(recipe=ricetta)
    token = request.COOKIES.get('comment_token')  # Ottieni il token dal cookie
    context = {'ricetta':ricetta,'commenti':commenti, 'token':token}
    return render(request,'blog/lista_commenti.html',context)

def lista_commenti_articoli(request,id_articolo):
    # list comment of a specifica article
     
    articolo = Article.objects.get(id=id_articolo)
    commenti = Comment.objects.filter(article=articolo)
    token = request.COOKIES.get('comment_token')  # Ottieni il token dal cookie
    context = {'articolo':articolo,'commenti':commenti, 'token':token}
    return render(request,'blog/lista_commenti_articoli.html',context)

def add_comment(request, recipe_id):
    # call form for adding a recipe or save it in return

    # Recupera la ricetta specifica
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Crea o recupera il token dal cookie
    token = request.COOKIES.get('comment_token')
    if not token:
        token = str(uuid.uuid4())

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # Crea il commento e lo associa alla ricetta e al token
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.token = token
            comment.save()

            # Risponde con un redirect o JSON per aggiornare la lista commenti
            #response = JsonResponse({'message': 'Commento aggiunto con successo!'})
            response = redirect('blog:lista_commenti', id_ricetta=recipe.id)
            response.set_cookie('comment_token', token)  # Imposta il token nel cookie
            return response
    else:
        form = CommentForm()

    # Ritorna la pagina della form per inserire il commento
    return render(request, 'blog/add_comment.html', {'form': form, 'recipe': recipe})

def add_comment_articolo(request, articolo_id):
# inserisce un commento ad un articolo o lo salva in risposta

    # Recupera l'articolo specifico
    articolo = get_object_or_404(Article, id=articolo_id)

    # Crea o recupera il token dal cookie
    token = request.COOKIES.get('comment_token')
    if not token:
        token = str(uuid.uuid4())

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # Crea il commento e lo associa alla ricetta e al token
            comment = form.save(commit=False)
            comment.article = articolo
            comment.token = token
            comment.save()

            # Risponde con un redirect o JSON per aggiornare la lista commenti
            #response = JsonResponse({'message': 'Commento aggiunto con successo!'})
            response = redirect('blog:lista_commenti_articoli', id_articolo=articolo.id)
            response.set_cookie('comment_token', token)  # Imposta il token nel cookie
            return response
    else:
        form = CommentForm()

    # Ritorna la pagina della form per inserire il commento
    return render(request, 'blog/add_comment_articolo.html', 
                  {'form': form, 'articolo': articolo, 'titolo':articolo.title})


def delete_comment(request, comment_id):
    # delete a recipe or article comment

    # Recupera il commento specifico
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Recupera il token dell'utente dal cookie
    token = request.COOKIES.get('comment_token')

    # Verifica che il token dell'utente corrisponda al token del commento
    if token != comment.token:
        # Se i token non corrispondono, l'utente non è autorizzato a eliminare il commento
        return HttpResponseForbidden("Non hai i permessi per eliminare questo commento.")

    # Se il token è corretto, elimina il commento
    comment.delete()

    # Redirect alla lista dei commenti della ricetta
    return redirect('blog:lista_commenti', id_ricetta=comment.recipe.id)

def update_comment(request, comment_id):
    # open form for updating a recipe or an article, ora update it
    # parameter 'tipo' tell which of that to use. 'art' an article, recipe otherwise

    # Recupera il commento specifico
    comment = get_object_or_404(Comment, id=comment_id)
    tipo =request.GET.get('tipo')
    # Recupera il token dell'utente dal cookie
    token = request.COOKIES.get('comment_token')

    # Verifica che il token dell'utente corrisponda al token del commento
    if token != comment.token:
        # Se i token non corrispondono, l'utente non è autorizzato a modificare il commento
        return HttpResponseForbidden("Non hai i permessi per modificare questo commento.")
    
    # Se la richiesta è POST, significa che l'utente ha inviato la form per l'aggiornamento
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()  # Salva il commento aggiornato
            if tipo == "art":
               return redirect('blog:lista_commenti_articoli', id_articolo=comment.article.id)
            else:
               return redirect('blog:lista_commenti', id_ricetta=comment.recipe.id)  # Redirect alla lista dei commenti

    # Se la richiesta è GET, precompiliamo la form con i dati del commento esistente
    else:
        form = CommentForm(instance=comment)
  
    if tipo == 'art':
        template = 'blog/add_comment_articolo.html'
        titolo = Article.objects.get(id=comment.article.id).title
    else:
        template = 'blog/add_comment.html'
        titolo = Recipe.objects.get(id=comment.recipe.id).title
    return render(request, template, {'form': form, 'comment': comment, 'titolo':titolo})

def videoricette(request):
    video = Video.objects.all()
   
    context = {'video':video}
    template_name ='blog/videoricette.html'
    return render(request,template_name,context)

def visitor(request):
    visitor = Visitor.objects.all()
    num_visitor = len(visitor)
    tot_visite = 0
    for v in visitor:
        tot_visite += v.visit_count
    context = {'num_visitor':num_visitor, 'tot_visite':tot_visite}
    template = 'blog/visitor.html'
    return render(request,template,context)