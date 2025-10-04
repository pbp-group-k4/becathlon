from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class TailwindMixin:
    """Apply Tailwind utility classes to form widgets."""

    input_classes = (
        'mt-1 block w-full rounded-xl border border-white/10 bg-slate-900/70 '
        'px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 '
        'focus:border-brand.sky focus:outline-none focus:ring-2 focus:ring-brand.sky/60'
    )

    def _apply_tailwind(self):
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing} {self.input_classes}".strip()
            field.widget.attrs.setdefault('placeholder', field.label)


class LoginForm(TailwindMixin, AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()


class RegistrationForm(TailwindMixin, UserCreationForm):
    first_name = forms.CharField(label='First name', max_length=150, required=False)
    last_name = forms.CharField(label='Last name', max_length=150, required=False)
    email = forms.EmailField(label='Email address', required=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default help texts for a cleaner UI
        for field_name in ['password1', 'password2']:
            self.fields[field_name].help_text = ''
        self._apply_tailwind()

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email
