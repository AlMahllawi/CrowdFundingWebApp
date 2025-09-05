from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search projects",
                "class": "form-control",
            }
        ),
    )
