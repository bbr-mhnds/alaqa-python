from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0020_merge_20250206_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorverification',
            name='email_code',
            field=models.CharField(default='000000', max_length=6),
        ),
    ] 