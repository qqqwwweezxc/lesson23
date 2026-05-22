from django import forms


class LoginForm(forms.Form):
    """Form for login."""
    name = forms.CharField(max_length=100)
    age = forms.IntegerField(min_value=1)