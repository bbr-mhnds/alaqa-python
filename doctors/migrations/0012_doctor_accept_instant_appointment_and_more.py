# Generated by Django 5.0.1 on 2025-02-02 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0011_pricecategory_doctordurationprice'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='accept_instant_appointment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='doctor',
            name='accept_tamkeen_clinics',
            field=models.BooleanField(default=False),
        ),
    ]
