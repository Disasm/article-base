from django.db import models, connection
from django.contrib.auth.models import User
from django.conf import settings

class TagManager(models.Manager):
    def subitems_ids(self, tags):
        ids = []
        for tag in tags:
            ids.append(str(tag.id))
        n = len(ids)
        ids = ", ".join(ids)

        cursor = connection.cursor()
        cursor.execute("""
            SELECT item_id FROM web_itemtag
            WHERE tag_id IN (%s) GROUP BY item_id
            HAVING count(*) = %d""" % (ids, n))
        ids = []
        for row in cursor.fetchall():
            ids.append(int(row[0]))
        return ids

    def subitems(self, tags):
        ids = self.subitems_ids(tags)
        return self.get_queryset().filter(id__in=ids)

    def subtags_ids(self, tags):
        ids = self.subitems_ids(tags)
        ids = ", ".join(ids)

        cursor = connection.cursor()
        cursor.execute("""
            SELECT tag_id, COUNT(*) FROM web_itemtag
            WHERE item_id IN (%s) GROUP BY tag_id""" % ids)
        result = {}
        for row in cursor.fetchall():
            result[int(row[0])] = int(row[1])
        return result

    def subtags(self, tags):
        ids = self.subtags_ids(tags)
        return self.get_queryset().filter(id__in=ids)

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User)

    def subtags(self, tags):
        return []

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

    def tag_list(self):
        return self.tags.all()

    def tag_string(self):
        tags = self.tags.all()
        names = []
        for tag in tags:
            names.append(tag.name)
        names = sorted(names)
        return ", ".join(names)

class ItemTag(models.Model):
    item = models.ForeignKey(Item)
    tag = models.ForeignKey(Tag)

