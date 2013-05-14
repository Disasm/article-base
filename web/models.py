from django.db import models, connection
from django.contrib.auth.models import User
from django.conf import settings

class TagManager(models.Manager):
    pass

class SubItemsManager(TagManager):
    def get(self, tags):
        ids = self.subitems_ids(tags)
        return self.get_queryset().filter(id__in=ids)

class SubTagsManager(TagManager):
    def get(self, tags):
        ids = self.subtags_ids(tags)
        return self.get_queryset().filter(id__in=ids.keys())

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User)
    
    @staticmethod
    def subitems_ids(tags):
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
    
    @staticmethod
    def subtags_ids(tags):
        ids = Tag.subitems_ids(tags)
        ids = map(str, ids)
        ids = ", ".join(ids)

        cursor = connection.cursor()
        cursor.execute("""
            SELECT tag_id, COUNT(*) FROM web_itemtag
            WHERE item_id IN (%s) GROUP BY tag_id""" % ids)
        result = {}
        for row in cursor.fetchall():
            result[int(row[0])] = int(row[1])
        return result

    @staticmethod
    def subtags(tags):
        old_ids = []
        for tag in tags:
            old_ids.append(tag.id)

        d = Tag.subtags_ids(tags)

        tags = Tag.objects.filter(id__in=d.keys()).order_by('name')

        # Filter out old tags
        tags2 = []
        for tag in tags:
            if int(tag.id) not in old_ids:
                tags2.append(tag)
        tags = tags2

        for tag in tags:
            tag.count = d[tag.id]

        return tags
    
    @staticmethod
    def with_counts(owner):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT tag_id, COUNT(*) FROM web_itemtag
            GROUP BY tag_id""")
        d = {}
        for row in cursor.fetchall():
            d[int(row[0])] = int(row[1])
        
        tags = Tag.objects.filter(id__in=d.keys()).order_by('name')
        for tag in tags:
            tag.count = d[tag.id]

        return tags

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
    
    @staticmethod
    def subitems(tags):
        ids = Tag.subitems_ids(tags)

        return Item.objects.filter(id__in=ids)

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
    owner = models.ForeignKey(User)

