# Generated by Django 4.2.11 on 2024-04-23 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_app', '0005_uploadedfile_public_alter_uploadedfile_incident_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='comment',
            field=models.TextField(blank=True),
        ),
    ]
