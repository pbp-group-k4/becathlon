from django import forms
from apps.main.models import ProductType


class ProductFilterForm(forms.Form):
    """Form for filtering products in catalog"""
    
    SORT_CHOICES = [
        ('newest', 'Newest First'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('name_asc', 'Name: A to Z'),
        ('name_desc', 'Name: Z to A'),
    ]
    
    categories = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Categories'
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        label='Min Price'
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        label='Max Price'
    )
    
    in_stock_only = forms.BooleanField(
        required=False,
        initial=False,
        label='In Stock Only'
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='newest',
        label='Sort By'
    )
    
    search = forms.CharField(
        required=False,
        max_length=200,
        label='Search Products'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate categories from ProductType
        product_types = ProductType.objects.all()
        self.fields['categories'].choices = [(pt.id, pt.name) for pt in product_types]
