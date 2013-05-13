from web.models import Tag, Item, ItemTag
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    pass

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
    return render('items.html', {'item_list': items}, context_instance=RequestContext(request))

# show item
@login_required
def item_show(request, id):
    id = int(id)
    item = get_object_or_404(Item, pk=id)
    return render(request, 'item.html', {'item': item})
