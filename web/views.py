from web.models import Tag, TagKind, Item, ItemTag
from web.forms import AddItemForm, EditItemForm, DeleteItemForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import os
import os.path
import hashlib
from datetime import datetime
from django.utils.timezone import utc

def paginator_post_process(page, delta = 3):
    current = page.number
    total = page.paginator.num_pages

    if total < 1:
        return page

    # collect page numbers
    s = set()
    for i in range(delta):
        s.add(i + 1)
    for i in range(total - delta, total):
        s.add(i + 1)
    for i in range(current - delta + 1, current + delta):
        s.add(i)

    # filter page numbers
    s2 = set()
    for e in s:
        if e >= 1 and e <= total:
            s2.add(e)

    # get separators
    l = []
    for e in s2:
        if (e-1) not in s2:
            l.append(-1)
        l.append(e)
    l.remove(-1)

    page.paginator.page_numbers = l
    return page

def get_tag(name, kind):
    try:
        tag = Tag.objects.get(name=name)
        return tag
    except ObjectDoesNotExist:
        kind_obj = None
        if kind != None:
            try:
                kind_obj = TagKind.objects.get(name=kind)
            except ObjectDoesNotExist:
                kind_obj = TagKind()
                kind_obj.name = kind
                kind_obj.description = "{kind_%s}" % kind
                kind_obj.icon = "{kind_icon_%s}" % kind
                kind_obj.save()

        tag = Tag()
        tag.name = name
        tag.kind = kind_obj
        tag.save()
        return tag

def fill_tags(item, tag_map):
    tags = []
    for kind in tag_map.keys():
        l = tag_map[kind].split(',')
        for tag in l:
            tag = tag.strip()
            if len(tag) > 0:
                tags.append((tag, kind))
    tags = sorted(list(set(tags)))
    if len(tags)==0:
        tags.append(('unknown', None))

    # remove old tags
    ItemTag.objects.filter(item=item).delete()

    # add new tags
    for (name, kind) in tags:
        tag = get_tag(name, kind)
        ItemTag.objects.create(item=item, tag=tag)

# get tag cloud
@login_required()
def get_tags(request):
    tags = Tag.with_counts()
    return render(request, 'tags.html', {'tags': tags})

# get item list and subtags
@login_required
def get_tag_items(request, tags):
    l = tags.split(",")
    ids = []
    for v in l:
        ids.append(int(v))
    ids = sorted(list(set(ids)))
    tags = Tag.objects.filter(id__in=ids)
    current_tags = tags
    
    # Construct current taglist string
    ids = []
    for tag in tags:
        ids.append(tag.id)
    tids = ",".join(map(str, ids))
    if len(tids)>0:
        tids = tids + ","

    # Get subtags
    subtags = Tag.subtags(tags)


    # Get items by subtags
    latest_item_list = Item.subitems(tags).order_by('-updated')
    size = len(latest_item_list)
    
    # Filter tag list
    tags = []
    for tag in subtags:
        if tag.count != size:
            tags.append(tag)
    subtags = tags
   
    # Build pagination
    page = request.GET.get('page')
    paginator = Paginator(latest_item_list, 10)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)
    
    items = paginator_post_process(items)
    return render(request, 'tag_items.html', {'tags': subtags, 'tids': tids, 'items': items, 'current_tags': current_tags})

# add new item
@login_required
def item_add(request):
    if request.method == 'POST':
        form = AddItemForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data

            name = request.FILES['file'].name

            f = request.FILES['file']
            m = hashlib.md5()
            m.update(os.urandom(32))
            m.update(name.encode('utf8'))
            uid = m.hexdigest()

            dir_path = os.path.join(settings.STATIC_ROOT, 'files', uid)
            os.mkdir(dir_path)
            path = os.path.join(dir_path, name)

            with open(path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            item = Item()
            item.name = cd['name']
            item.description = cd['description']
            item.filename = f.name
            item.size = f.size
            item.uid = uid
            item.created = datetime.utcnow().replace(tzinfo=utc)
            item.updated = datetime.utcnow().replace(tzinfo=utc)
            item.save()

            tags = {}
            if cd['year'] is None:
                tags['year'] = ""
            else:
                tags['year'] = str(cd['year'])
            tags['people'] = cd['authors']
            tags['company'] = cd['company']
            tags['type'] = cd['kind']
            tags[None] = cd['tags']
            fill_tags(item, tags)

            return HttpResponseRedirect('/item/%d' % item.id)
    else:
        form = AddItemForm() # An unbound form
    return render(request, 'item_add.html', {'form': form, 'edit': False})

# edit item
@login_required
def item_edit(request, id):
    id = int(id)
    item = get_object_or_404(Item, pk=id)
    if request.method == 'POST':
        form = EditItemForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            item.name = cd['name']
            item.description = cd['description']
            item.updated = datetime.utcnow().replace(tzinfo=utc)
            item.save()

            tags = {}
            tags[None] = cd['tags']
            fill_tags(item, tags)

            return HttpResponseRedirect('/item/%d' % item.id)
    else:
        form = EditItemForm(initial={'name': item.name, 'description': item.description, 'tags': item.tag_string()})
    return render(request, 'item_add.html', {'form': form, 'edit': True})

# delete item
@login_required
def item_delete(request, id):
    id = int(id)
    item = get_object_or_404(Item, pk=id)
    if request.method == 'POST':
        # delete file
        dir_path = os.path.join(settings.STATIC_ROOT, 'files', item.uid)
        path = os.path.join(dir_path, item.filename)
        try:
            os.unlink(path)
        except:
            pass
        try:
            os.rmdir(path)
        except:
            pass

        # delete from database
        item.delete()

        return HttpResponseRedirect('/items/')
    else:
        form = DeleteItemForm()
    return render(request, 'item_delete.html', {'form': form, 'item': item})

# get item list
@login_required
def item_list(request):
    page = request.GET.get('page')
    latest_item_list = Item.objects.all().order_by('-created')
    paginator = Paginator(latest_item_list, 10)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)

    items = paginator_post_process(items)
    return render(request, 'items.html', {'items': items})

# show item
@login_required
def item_show(request, id):
    id = int(id)
    item = get_object_or_404(Item, pk=id)
    return render(request, 'item.html', {'item': item})
