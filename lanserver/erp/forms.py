from django import forms
from multiupload.fields import MultiFileField

class EmailForm(forms.Form):
    from_email = forms.EmailField()
    to_email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    body = forms.CharField(widget=forms.Textarea)
    attachments = MultiFileField(min_num=0, max_num=10, max_file_size=1024 * 1024 * 200)