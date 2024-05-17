from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.views.generic import FormView
from .views import file_upload_view

from . import views

app_name = "whistleblower"

urlpatterns = [
    #path('accounts/', include('allauth.urls')),
    #path('logout', LogoutView.as_view()),
    path('file_upload/', file_upload_view, name='file_upload')
]