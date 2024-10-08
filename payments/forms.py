from django import forms
from test_logic.models import Test

class ImportQuestionsForm(forms.Form):
    json_file = forms.FileField(label='Select JSON file')
    test = forms.ModelChoiceField(queryset=Test.objects.all(), label='Select Test')
