# Generated by Django 5.0.1 on 2025-02-08 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_alter_appointment_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='completion_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='completion_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='duration_minutes',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
