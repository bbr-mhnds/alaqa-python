from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0016_fix_doctor_verification_schema'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop the existing table
            "DROP TABLE IF EXISTS doctors_doctorverification;",
            # No reverse SQL needed since we're recreating the table
            None
        ),
        migrations.CreateModel(
            name='DoctorVerification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=17)),
                ('email_verified', models.BooleanField(default=True)),
                ('phone_verified', models.BooleanField(default=False)),
                ('registration_data', models.JSONField(default=dict)),
                ('license_document', models.FileField(null=True, upload_to='temp/license_documents/')),
                ('qualification_document', models.FileField(null=True, upload_to='temp/qualification_documents/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_used', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ] 