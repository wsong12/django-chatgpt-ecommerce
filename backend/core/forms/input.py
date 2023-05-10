# --------------------------------------------------------------
# Django imports
# --------------------------------------------------------------
from django import forms


class InputForm(forms.Form):
    '''
    Basic form for our animal name suggestion form and logo generator form
    '''

    input = forms.CharField(max_length=100, required=True,
      widget=forms.TextInput(attrs={
        'placeholder': 'What is the product you want to sell..'}))

    class Meta:
        fields = ('input',)



class InputFormName(forms.Form):
    '''
    Basic form for our animal name suggestion form and logo generator form
    '''

    input = forms.CharField(max_length=100, required=True,
      widget=forms.TextInput(attrs={
        'placeholder': 'Give us a description of the product you want to sell..'}))

    class Meta:
        fields = ('input',)