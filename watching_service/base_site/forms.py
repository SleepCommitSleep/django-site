from django import forms
from .models import Film, Video, Feed


class FilmForm(forms.ModelForm):
    poster_img_link = forms.URLField(
        required=False
    )

    class Meta:
        model = Film
        fields = "__all__"
        widgets = {'description': forms.Textarea()}


class FilmMediaForm(forms.ModelForm):
    video_url = forms.URLField(
        required=False
    )

    class Meta:
        model = Video
        fields = "__all__"


class FeedForm(forms.ModelForm):
    class Meta:
        model = Feed
        exclude = "__all__"
        widgets = {"film_id": forms.NumberInput, "update_comment": forms.Textarea}
