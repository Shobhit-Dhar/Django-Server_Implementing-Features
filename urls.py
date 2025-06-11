from django.urls import path
from .views import AudioTranscriptionView, TitleSuggestionView

urlpatterns = [
    path('transcribe/', AudioTranscriptionView.as_view(), name='audio-transcription'),
    path('suggest-title/', TitleSuggestionView.as_view(), name='title-suggestion'),
]