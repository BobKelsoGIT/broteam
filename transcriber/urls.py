from django.conf import settings
from django.conf.urls.static import static
from .views import upload_and_transcribe
from django.urls import path

urlpatterns = [
    path('', upload_and_transcribe, name='transcribe'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
