# Generated by Django 5.0.1 on 2025-01-30 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0006_alter_doctorverification_sms_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='bank_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='doctor',
            name='swift_code',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='account_holder_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='iban_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='doctorverification',
            name='sms_code',
            field=models.CharField(max_length=10),
        ),
    ]
