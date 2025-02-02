# Generated by Django 5.0.1 on 2025-01-30 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instant_appointment_prices', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='instantappointmentprice',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='instantappointmentprice',
            name='site_type',
            field=models.CharField(default='clinic', help_text='Type of site for the appointment', max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='instantappointmentprice',
            unique_together={('duration', 'site_type')},
        ),
    ]
