from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0027_fix_null_license_numbers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='license_number',
            field=models.CharField(
                max_length=255,
                unique=True,
                null=False,
                blank=False,
            ),
        ),
        migrations.RunSQL(
            sql='''
            ALTER TABLE doctors_doctor 
            ADD CONSTRAINT check_license_number_not_empty 
            CHECK (length(trim(license_number)) > 0);
            ''',
            reverse_sql='''
            ALTER TABLE doctors_doctor 
            DROP CONSTRAINT IF EXISTS check_license_number_not_empty;
            '''
        ),
    ] 