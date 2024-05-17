"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic import FormView
from django.contrib.auth.views import LogoutView
from oauth_app import views
from oauth_app.views import file_upload_view, list_files_view, list_submissions_view, submission_detail_view, user_submissions_view, resources_view, delete_submission, public_submissions_view, print_submission
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', TemplateView.as_view(template_name="account/login.html"), name='custom_login'),
    path('', views.index, name='login'),
    path('accounts/', include('allauth.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('file_upload/', file_upload_view, name='file_upload'),
    path('success/',TemplateView.as_view(template_name='successful_submission.html')),
    path('list_files/', list_submissions_view, name='list_files'),
    path('submissions/', list_submissions_view, name='list-submissions'),
    path('submissions/<int:submission_id>/', submission_detail_view, name='view-submission'),
    path('my_submissions/',user_submissions_view, name='view-my-submissions'),
    path('resources/', resources_view, name='resources'),
    path('delete/<int:submission_id>/', delete_submission, name='delete-submission'),
    path('public_submissions/', public_submissions_view, name='public-submissions'),
    path('submissions/print/<int:submission_id>/', print_submission, name='print_submission'),
]
