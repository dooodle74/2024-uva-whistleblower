# oauth_app/views.py
from django.utils import timezone
import boto3
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from reportlab.lib.units import inch

from mysite import settings

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import UploadedFile
from django.shortcuts import get_object_or_404, render
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import UploadedFile
from django.conf import settings
import io


@login_required
def index(request):
    context = {
        'is_site_admin': request.user.groups.filter(name='Site Admins').exists()
    }
    if request.user.groups.filter(name='Site Admins').exists():
        return render(request, 'admin_user.html')
    else:
        return render(request, 'user.html')

def file_upload_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        form.fields['question_5'].widget.attrs['max'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        if form.is_valid():
            # Handle the file here. For example, save it to the database or the file system
            #handle_uploaded_file(request.FILES['file'])

            uploaded_file = UploadedFile()
            if 'other' in form.cleaned_data['question_1']:
                incident_type = form.cleaned_data['question_1']
                if form.cleaned_data['question_1_other']:
                    incident_type.remove('other')
                    incident_type.append(f"Other: {form.cleaned_data['question_1_other']}")

            else:
                incident_type = form.cleaned_data['question_1']

            if 'other' in form.cleaned_data['question_2']:
                organizations_involved = "Other: " + form.cleaned_data['question_2_other']
            else:
                organizations_involved = form.cleaned_data['question_2']

            uploaded_file.incident_type = incident_type
            uploaded_file.organizations_involved = organizations_involved
            uploaded_file.injuries = form.cleaned_data['question_4']
            uploaded_file.date_and_time = form.cleaned_data['question_5']
            uploaded_file.additional_info = form.cleaned_data['additional_info']
            uploaded_file.who_was_involved = form.cleaned_data['question_3']

            if 'file' in request.FILES:
                uploaded_file.file = request.FILES['file']
            # Associate the file with the current user if authenticated
            uploaded_file.user = request.user if request.user.is_authenticated else None

            # Now save the instance to the database
            uploaded_file.save()
            if request.user.is_authenticated:
                uploaded_file.user = request.user
            else:
                user = get_user_model()
                anonymous_user, created = user.objects.get_or_create(username='anonymous')
                uploaded_file.user = anonymous_user
            uploaded_file.save()
            return HttpResponseRedirect('/success/')  # Redirect to a new URL
    else:
        form = UploadFileForm()  # An empty form for a GET request
        form.fields['question_5'].widget.attrs['max'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
    return render(request, 'file_upload.html', {'form': form})

"""
def handle_uploaded_file(f):
    with open('file_name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)"""

def add_is_site_admin(request):
    return {
        'is_site_admin': request.user.groups.filter(name='Site Admins').exists() if request.user.is_authenticated else False
    }

def list_files_view(request):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='us-east-2'
    )
    pre_signed_urls = []

    for file in UploadedFile.objects.all():
        user_name = file.user.username if file.user else "Anonymous"
        pre_signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': "static/"+file.file.name,
            },
            ExpiresIn=3600
        )
        pre_signed_urls.append((pre_signed_url, file.file.name, user_name))

    return render(request, 'list_files.html', {'file_urls': pre_signed_urls})


def list_submissions_view(request):
    status_filter = request.GET.get('status')
    privacy_filter = request.GET.get('privacy')
    submissions = UploadedFile.objects.filter().order_by('-upload_time')
    if status_filter:
        submissions = submissions.filter(status=status_filter)

    if privacy_filter:
        if privacy_filter == 'Private':
            submissions = submissions.filter(public=False)
        elif privacy_filter == 'Public':
            submissions = submissions.filter(public=True)
    request.session['last_page'] = request.path
    return render(request, 'list_submissions.html', {'submissions': submissions, 'current_status': status_filter if status_filter else 'All',  'current_privacy': privacy_filter if privacy_filter else 'All'})


#changed
def user_submissions_view(request):
    status_filter = request.GET.get('status')
    if status_filter:
        submissions = UploadedFile.objects.filter(status=status_filter, user=request.user).order_by('-upload_time')
    else:
        submissions = UploadedFile.objects.filter(user=request.user).order_by('-upload_time')
    request.session['last_page'] = request.path
    return render(request, 'user_submissions.html', {'submissions': submissions, 'current_status': status_filter if status_filter else 'All'})


def delete_submission(request, submission_id):
    submission = UploadedFile.objects.get(id=submission_id)
    if request.user == submission.user: #only deletes if this is the user who submitted it
        submission.delete()
    return redirect('view-my-submissions')


def submission_detail_view(request, submission_id):
    last_page = request.session.get('last_page', '')
    admin = request.user.groups.filter(name='Site Admins').exists()
    submission = UploadedFile.objects.get(id=submission_id)
    is_user = submission.user == request.user
    public = submission.public

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='us-east-2'
    )

    file_url = None
    if submission.file:
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': "static/"+submission.file.name,
            },
            ExpiresIn=3600
        )

    if request.method == 'POST':
        status = request.POST.get('status')
        comment = request.POST.get('comment')
        public = request.POST.get('public') == 'true'
        # Update submission status and comment
        submission.status = status
        submission.comment = comment
        submission.public = public
        submission.save()
        return redirect(last_page)  # Redirect back to the list of submissions after updating
    if request.user.groups.filter(name='Site Admins').exists() and submission.status == 'New':
        submission.status = 'In Progress'
        submission.save()

    return render(request, 'submission_detail.html', {
        'submission': submission,
        'file_url': file_url,
        'status': submission.status,  # Pass status back to the template
        'comment': submission.comment,  # Pass comment back to the template
        'admin':admin,
        'is_user': is_user,
        'public':public,
        'last_page':last_page,
        'file_name':submission.file.name
    })
   # return render(request, 'submission_detail.html', {'submission': submission})


def resources_view(request):
    return render(request, 'resources.html')

def public_submissions_view(request):
    submissions = UploadedFile.objects.filter(public=True).order_by('-upload_time')
    # From ChatGPT 4
    # query:
    # how would I remember the most recent page a user has been to in Django without passing a string into the url?
    request.session['last_page'] = request.path
    return render(request, 'list_public_submissions.html', {'submissions':submissions})


def print_submission(request, submission_id):
    submission = get_object_or_404(UploadedFile, pk=submission_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y_position = height - inch
    p.setFont("Helvetica-Bold", 14)

    p.drawString(inch, y_position, f"Misconduct Report")
    y_position -= 0.2 * inch
    p.setFont("Helvetica", 11)
    p.drawString(inch, y_position, f"Submitted by {request.user}")

    y_position -= 0.5 * inch

    p.setFont("Helvetica", 12)
    #  Incident type
    if submission.incident_type:
        readable_incident_type = ', '.join(submission.get_readable_incident_type())
        p.drawString(inch, y_position, f"Incident Type: {readable_incident_type}")
        y_position -= 0.5 * inch

        #  Organizations Involved
    if submission.organizations_involved:
        organizations = submission.get_organizations_involved_display()
        p.drawString(inch, y_position, f"Organizations Involved: {organizations}")
        y_position -= 0.5 * inch

        #  Who Was Involved
    if submission.who_was_involved:
        p.drawString(inch, y_position, f"Who Was Involved: {submission.who_was_involved}")
        y_position -= 0.5 * inch

        #  Injuries/Damages Inflicted
    if submission.injuries:
        p.drawString(inch, y_position, f"Injuries/Damages Inflicted: {submission.injuries}")
        y_position -= 0.5 * inch

        #  Date and Time
    if submission.date_and_time:
        p.drawString(inch, y_position, f"Date and Time: {submission.date_and_time}")
        y_position -= 0.5 * inch

        #  Additional Information
    if submission.additional_info:
        p.drawString(inch, y_position, f"Additional Information: {submission.additional_info}")
        y_position -= 0.5 * inch
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="submission_report.pdf"'
    return response