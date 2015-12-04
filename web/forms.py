# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings

class AddItemForm(forms.Form):
    name = forms.CharField(label="Название", max_length=500)
    description = forms.CharField(label="Описание", max_length=200, required=False)

    kinds = ['статья', 'презентация', 'книга']
    kinds = tuple(zip(kinds, kinds)) + (('', 'другой'),)
    kind = forms.ChoiceField(label="Тип", choices=kinds, required=False)
    year = forms.DecimalField(label="Год издания", max_value=9999, required=False)
    authors = forms.CharField(label="Авторы", max_length=500, required=False)
    company = forms.CharField(label="Коллектив", max_length=200, required=False)
    tags = forms.CharField(label="Теги", max_length=500, required=False)
    file = forms.FileField()
    
    def clean_file(self):
        file = self.cleaned_data['file']
        
        if len(file.name.split('.')) == 1:
            raise forms.ValidationError('File type is not supported')

        ext = file.name.split('.')[-1].lower()
        if ext not in settings.ALLOWED_EXTS:
            raise forms.ValidationError('File type is not supported')

        return file

class EditItemForm(forms.Form):
    name = forms.CharField(max_length=500)
    description = forms.CharField(max_length=200, required=False)
    tags = forms.CharField(max_length=500, required=False)

class DeleteItemForm(forms.Form):
    pass

