# urls.py

from django.urls import path
from .views import FileUploadView, tts, LetterFileUploadView, WordFileUploadView, PhraseFileUploadView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('uploadLetter/', LetterFileUploadView.as_view(), name='letter-upload'),
    path('uploadWord/', WordFileUploadView.as_view(), name='word-upload'),
    path('uploadPhrase/', PhraseFileUploadView.as_view(), name='phrase-upload'),
    path('tts/', tts, name='tts'),
    #path('filter-noise/', filter_noise_view, name='filter_noise'),
]
