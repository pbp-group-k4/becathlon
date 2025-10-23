from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "phone","email","preferred_sports", "profile_picture", "newsletter_opt_in"]
        widgets = {
            "preferred_sports": forms.TextInput(attrs={"placeholder": "e.g. football, running"}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if phone and not phone.replace("+","").replace(" ","").replace("-","").isdigit():
            raise forms.ValidationError("Phone must contain only digits, spaces, + or -.")
        return phone
    def clean_newsletter_opt_in(self):
        newsletter_opt_in = self.cleaned_data.get("newsletter_opt_in")
        if newsletter_opt_in is None:
            raise forms.ValidationError("This field is required.")
        return newsletter_opt_in

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        classes = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = classes
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['class'] = classes
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['email'].widget.attrs['class'] = classes
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email address'
        self.fields['phone'].widget.attrs['class'] = classes
        self.fields['phone'].widget.attrs['placeholder'] = '+1 (555) 000-0000'
        self.fields['preferred_sports'].widget.attrs['class'] = classes
        self.fields['preferred_sports'].widget.attrs['placeholder'] = 'e.g. football, running, cycling'
        self.fields['profile_picture'].widget.attrs['class'] = classes
        self.fields['newsletter_opt_in'].widget.attrs['class'] = ''