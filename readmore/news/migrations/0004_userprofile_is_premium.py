# Generated by Django 5.1.6 on 2025-04-17 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_manualtask_button_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_premium',
            field=models.BooleanField(default=False, help_text='Premium members earn double points.'),
        ),
    ]
