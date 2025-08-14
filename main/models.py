from django.db import models
from django.db.models import Model


class Beermat(models.Model):
    photo_mat = models.ImageField(upload_to='beermats/', blank=True, null=True, default='beermats/default.png')
    maker = models.CharField('Maker', max_length=50, blank=True)
    name = models.CharField('Name', max_length=50, blank=True)
    country = models.CharField('Country', max_length=50, blank=True)
    weight = models.FloatField('Weight (g)', null=True, blank=True)
    diameter = models.FloatField('Diameter (mm)', null=True)
    thickness = models.FloatField('Thickness (mm)', null=True)
    #when = models.DateTimeField('When', null=True, blank=True)
    #where = models.CharField('where', max_length=50, blank=True)
    #description = models.TextField('Description', max_length=500, blank=True)
    # function 'where and 'when' will be available only in 'my collection' to add

    def __str__(self):
        return f"{self.maker}, {self.name}"