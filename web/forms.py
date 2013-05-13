from django import forms
from django.conf import settings

class AddItemForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=200, required=False)
    tags = forms.CharField(max_length=200, required=False)
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
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=200, required=False)
    tags = forms.CharField(max_length=200, required=False)

