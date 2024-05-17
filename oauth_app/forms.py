from django.utils import timezone

from django import forms
from django.core.exceptions import ValidationError

class UploadFileForm(forms.Form):

    question_1 = forms.MultipleChoiceField(
        choices=[
            ('option1', 'Hazing'),
            ('option2', 'Sexual Misconduct'),
            ('option3', 'Verbal Abuse'),
            ('option4', 'Physical Abuse'),
            ('option5', 'Substance Abuse'),
            ('option6', 'Discrimination'),
            ('other', 'Other'),
        ],
        required=True,
        widget=forms.CheckboxSelectMultiple
    )
    question_1_other = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'question_1_other_info', 'placeholder': 'Other...'}))


    # Organizations involved
    question_2 = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('option1', 'None'),
            ('option2', 'Fraternity'),
            ('option3', 'Sorority'),
            ('option4', 'Academic Club'),
            ('option5', 'Non-Academic Club'),
            ('option6', 'Sports'),
            ('option7', 'Societies'),
            ('other', 'Other'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    question_2_other = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'question_2_other_info', 'placeholder': 'Other...'}))
    #Who was involved
    question_3 = forms.CharField(widget=forms.TextInput, required=False)
    #Injuries
    question_4 = forms.CharField(widget=forms.TextInput, required=False)
    # Time/ Date
    question_5 = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control datetimepicker-input',
            'id': 'datetimepicker',
            'max': ''
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=False
    )

    def clean_question_5(self):
        question_5 = self.cleaned_data.get('question_5')
        if question_5 and question_5 > timezone.now():
            raise ValidationError("Error: Provided a future time")
        return question_5

    """Used ChatGPT 3.5 to determine how to limit uploadable files to pdf txt and jpg
    "If I am creating a django app that allows users to upload files to amazon s3, how do I limit users to only be able to upload pdfs txts and jpgs"""
    #explain incident
    additional_info = forms.CharField(widget=forms.Textarea, required=True)
    #upload a file
    file = forms.FileField(required=False)
    def clean_file(self):
        file = self.cleaned_data['file']
        if file is not None:
            if not (file.name.endswith('.pdf') or file.name.endswith('.txt') or file.name.endswith('.jpg')):
                raise ValidationError("Only pdf, txt, or jpg files are allowed.")
        return file
