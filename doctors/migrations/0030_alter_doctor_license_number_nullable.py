from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0029_modify_license_constraint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='license_number',
            field=models.CharField(
                max_length=255,
                unique=True,
                null=True,
                blank=True,
                help_text='License number will be required for verification'
            ),
        ),
    ] 