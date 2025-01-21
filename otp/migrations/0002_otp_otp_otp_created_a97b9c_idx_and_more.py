# Generated by Django 5.0.1 on 2025-01-21 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='otp',
            index=models.Index(fields=['-created_at'], name='otp_otp_created_a97b9c_idx'),
        ),
        migrations.AddIndex(
            model_name='otp',
            index=models.Index(fields=['phone_number', 'is_verified'], name='otp_otp_phone_n_f26c53_idx'),
        ),
    ]
