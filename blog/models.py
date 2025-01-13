from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.timezone import now
import requests


class Category(models.Model):
    ordine = models.IntegerField(default=0) # ordinamento negli elenchi
    name = models.CharField(max_length=100)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name
    
    class Meta:
       ordering = ['ordine']

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # bio = models.TextField(blank=True, null=True)
    nome = models.CharField(max_length=100,null=True,blank=True)
    bio = RichTextUploadingField(default="")
    email = models.EmailField(max_length = 100,default='info@e20.website')
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    telefono = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.user.username

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField() # models.TextField()
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)  # Campo per il PDF

    def __str__(self):
        return self.title

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

TIME_UNITS = [
    ('min', 'Minuti'),
    ('hrs', 'Ore'),
]

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    descrizione_breve = models.CharField(max_length=200,blank=True,null=True)
    tempo_preparazione = models.FloatField(blank=True,null=True)
    tempo_preparazione_unita = models.CharField(
        max_length=3, choices=TIME_UNITS, default='min'
    ) 
    tempo_cottura = models.FloatField(blank=True,null=True)
    tempo_cottura_unita = models.CharField(
        max_length=3, choices=TIME_UNITS, default='min'
    ) 
    description  = RichTextUploadingField()  # models.TextField()
    instructions = RichTextUploadingField()  # models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    persone = models.IntegerField(default=2) # per quante persone sono le quantità degli ingredienti
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slideshow = models.BooleanField(default=False) # se da includere nello slide show


    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=100)
    unit = models.CharField(max_length=30,null=True,blank=True) 

class Immagini(models.Model):
    
    titolo = models.CharField(max_length=50,default='')
    immagine = models.ImageField()
    recipe = models.ForeignKey(Recipe,on_delete=models.CASCADE,blank=True,null=True)

    class Meta:
        ordering = ['titolo']
    
    def __str__(self):
        return self.titolo

class Comment(models.Model):
    author = models.CharField(max_length=100,null=True,blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    token = models.CharField(max_length=36,blank=True,null=True)  # UUID è lungo 36 caratteri
    rate = models.IntegerField(null=True,blank=True,default=3)

    def __str__(self):
        return f'Comment by {self.author} on {self.created_at}'

class Video(models.Model):
    titolo = models.CharField(max_length=200, blank=True,null=True)
    autore =  models.CharField(max_length=200, blank=True,null=True)
    data =  models.DateField(auto_now=False)
    visibile = models.BooleanField(default=True)
    descrizione = models.CharField(max_length=250, blank=True,null=True)
    embed = models.TextField(default='')

    def __str__(self):
        return self.titolo
    
    class Meta:
        ordering = ['-data']

### STATISTICHE DI VISITA

class Visitor(models.Model):
    # Identificatore unico per ciascun visitatore (ID sessione o indirizzo IP)

    ip_address = models.GenericIPAddressField(null=True, blank=True)  # l'indirizzo IP del visitatore
    visit_count = models.IntegerField(default=1)  # Numero di visite del visitatore
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    last_visit = models.DateTimeField(default=now)  # Data e ora dell'ultimo accesso

    def __str__(self):
        return f"Visitatore {self.ip_address} ha visitato {self.visit_count} volte"
    
    def update_location(self):
        #Aggiorna il paese, la regione e la città utilizzando l'IP
        api_url = f'http://ip-api.com/json/{self.ip_address}'
        response = requests.get(api_url)
        data = response.json()

        if data.get("status") == "fail":
            self.country = "Unknown"
            self.region = "Unknown"
            self.city = "Unknown"
        else:
            self.country = data.get("country", "Unknown")
            self.region = data.get("regionName", "Unknown")  # Regione (o provincia)
            self.city = data.get("city", "Unknown")  # Città
        self.save()
