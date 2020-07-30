from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
from category_api.models import Category

# Create your models here.
class Paper(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(blank=True, unique=True)
    abstract = models.TextField(null=True)
    type_paper = models.CharField(max_length=200, null=True, blank=True)
    isbn = models.CharField(max_length=200,null=True)
    issn = models.CharField(max_length=200,null=True)
    publishing_company = models.TextField(null=True)
    doi = models.CharField(max_length=200,null=True)
    pages = models.IntegerField(null=True)
    site = models.URLField(null=True)
    created_on = models.CharField(max_length=200,null=True)
    year = models.IntegerField(null=True)
    n_citation = models.IntegerField(default=0)
    n_version = models.IntegerField(default=1)
    rating = models.IntegerField(null=True,validators=[MinValueValidator(1), MaxValueValidator(5)])
    eprint = models.URLField(null=True)
    pdf = models.TextField(null=True)
    pdf_text = models.TextField(null=True)
    picture = models.URLField(null=True)
    added_on = models.DateTimeField(auto_now_add=True)
    mentioned_in = models.ManyToManyField("self",symmetrical=True)
    owns_version = models.ManyToManyField("self",symmetrical=True)
    references = models.TextField(null=True)
    original_references = models.TextField(null=True)
    #searched_for = models.ManyToManyField(Research)
    have_category = models.ManyToManyField(Category)
    #created_by = models.ManyToManyField(Writer)
    writers = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "paper"

    def __str__(self):
       return self.title