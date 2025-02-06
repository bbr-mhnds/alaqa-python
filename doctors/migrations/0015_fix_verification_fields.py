from django.db import migrations

def clear_verification_data(apps, schema_editor):
    DoctorVerification = apps.get_model('doctors', 'DoctorVerification')
    # Clear all existing verification records as they are temporary anyway
    DoctorVerification.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0014_remove_verification_codes'),
    ]

    operations = [
        migrations.RunPython(clear_verification_data),
    ] 