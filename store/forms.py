from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    SIZE_CHOICES = Product.SIZE_CHOICES

    available_sizes = forms.MultipleChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Product
        fields = '__all__'
