from web.models import Tag, Item, ItemTag
from web.forms import AddItemForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.conf import settings
import os
import os.path
import hashlib
from datetime import datetime

# get tag cloud
@login_required()
def get_tags(request):
    pass

# get item list and subtags
@login_required
def get_tag_items(request, tags):
    pass

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
            m.update(name)
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
            item.owner = request.user
            item.created = datetime.now()
            item.updated = datetime.now()
            item.save()

            return HttpResponseRedirect('/item/%d' % item.id)
    else:
        form = AddItemForm() # An unbound form
    return render(request, 'item_add.html', {'form': form, 'edit': False})

# edit item
@login_required
def item_edit(request, id):
    pass

# get item list
@login_required
def item_list(request):
    page = request.GET.get('page')
    latest_item_list = Item.objects.all().order_by('-updated')
    paginator = Paginator(latest_item_list, 10)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)
    return render(request, 'items.html', {'items': items})

# show item
@login_required
def item_show(request, id):
    id = int(id)
    item = get_object_or_404(Item, pk=id)
    return render(request, 'item.html', {'item': item})
