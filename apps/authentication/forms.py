from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    """Custom sign up form"""
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    account_type = forms.ChoiceField(
        choices=[('BUYER', 'Buyer - Browse and purchase items'), ('SELLER', 'Seller - Sell items on our marketplace')],
        required=True,
        widget=forms.RadioSelect,
        help_text='Choose whether you want to buy items or sell items on the Becathlon marketplace.'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'account_type', 'password1', 'password2')
