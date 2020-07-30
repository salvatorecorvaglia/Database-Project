from django.db import models

# Create your models here.
class Category(models.Model):
    label = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "category"

    def __str__(self):
       return self.label