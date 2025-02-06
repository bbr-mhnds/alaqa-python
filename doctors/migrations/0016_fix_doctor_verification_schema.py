from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0015_fix_verification_fields'),
    ]

    operations = [
        # First drop the problematic columns if they exist
        migrations.RemoveField(
            model_name='doctorverification',
            name='email_code',
        ),
        migrations.RemoveField(
            model_name='doctorverification',
            name='sms_code',
        ),
        # Recreate the model with correct fields
        migrations.AlterField(
            model_name='doctorverification',
            name='email_verified',
            field=models.BooleanField(default=True),  # Changed to default True since we're not using email verification
        ),
        migrations.AlterField(
            model_name='doctorverification',
            name='registration_data',
            field=models.JSONField(default=dict),
        ),
    ] 