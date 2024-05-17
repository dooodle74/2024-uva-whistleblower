from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.views.generic import TemplateView

from .models import UploadedFile
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LogoutView
from oauth_app.views import index, file_upload_view, list_files_view, list_submissions_view, submission_detail_view, user_submissions_view, resources_view, delete_submission, public_submissions_view, print_submission


class UploadedFileTest(TestCase):
    def setUp(self):
        self.test_file = SimpleUploadedFile('test_file.txt', b'this is the file.')
        self.uploaded_file = UploadedFile.objects.create(file=self.test_file)

    def test_file_field(self):
        file_instance = UploadedFile.objects.get(file='test_file.txt')
        self.assertEqual(file_instance.file.name, 'test_file.txt')

    def test_file_upload(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('file_upload'), {'file': self.test_file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UploadedFile.objects.count(), 1)


from django.contrib.auth.models import User, Group

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')
        self.test_user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        self.test_user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.group = Group.objects.create(name='Site Admins')
        self.test_user1.groups.add(self.group)

    def test_redirect_when_user_is_not_authenticated(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/')

    def test_authenticated_user_is_not_redirected(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_admin_user_sees_admin_template(self):
        self.client.login(username='testuser1', password='testpassword1')
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'admin_user.html')

    def test_non_admin_user_sees_user_template(self):
        self.client.login(username='testuser2', password='testpassword2')
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'user.html')

class URLTests(TestCase):
    def test_custom_login_url(self):
        path = reverse('custom_login')
        self.assertEqual(resolve(path).func.__name__, TemplateView.as_view(template_name="account/login.html").__name__)

    def test_login_url(self):
        path = reverse('login')
        self.assertEqual(resolve(path).func, index)

    def test_logout_url(self):
        path = reverse('logout')
        self.assertEqual(resolve(path).func.__name__, LogoutView.as_view().__name__)

    def test_file_upload_url(self):
        path = reverse('file_upload')
        self.assertEqual(resolve(path).func, file_upload_view)

    def test_list_files_url(self):
        path = reverse('list_files')
        self.assertEqual(resolve(path).func, list_submissions_view)

    def test_list_submissions_url(self):
        path = reverse('list-submissions')
        self.assertEqual(resolve(path).func, list_submissions_view)

    def test_view_submission_url(self):
        path = reverse('view-submission', kwargs={'submission_id': 1})
        self.assertEqual(resolve(path).func, submission_detail_view)

    def test_view_my_submissions_url(self):
        path = reverse('view-my-submissions')
        self.assertEqual(resolve(path).func, user_submissions_view)

    def test_resources_url(self):
        path = reverse('resources')
        self.assertEqual(resolve(path).func, resources_view)

    def test_delete_submission_url(self):
        path = reverse('delete-submission', kwargs={'submission_id': 1})
        self.assertEqual(resolve(path).func, delete_submission)

    def test_public_submissions_url(self):
        path = reverse('public-submissions')
        self.assertEqual(resolve(path).func, public_submissions_view)

    def test_print_submission_url(self):
        path = reverse('print_submission', kwargs={'submission_id': 1})
        self.assertEqual(resolve(path).func, print_submission)