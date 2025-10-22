from django import forms
from apps.main.models import Product

class AddToCartForm(forms.Form):
    """
    Form for adding items to cart
    """
    quantity = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.product and quantity > self.product.stock:
            raise forms.ValidationError(f"Only {self.product.stock} items available in stock.")
        return quantity

class UpdateQuantityForm(forms.Form):
    """
    Form for updating cart item quantity
    """
    quantity = forms.IntegerField(min_value=0, initial=1)

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.product and quantity > self.product.stock:
            raise forms.ValidationError(f"Only {self.product.stock} items available in stock.")
        return quantity