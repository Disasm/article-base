from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User)

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    filename = models.CharField(max_length=200)
    size = models.IntegerField()
    uid = models.CharField(max_length=50)
    owner = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag, through='ItemTag')
    created = models.DateTimeField()
    updated = models.DateTimeField()

    def url(self):
        return settings.STATIC_URL + "files/" + self.uid + "/" + self.filename;

class ItemTag(models.Model):
    item = models.ForeignKey(Item)
    tag = models.ForeignKey(Tag)

