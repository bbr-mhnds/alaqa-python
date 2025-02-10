from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0031_fix_license_final'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            ALTER TABLE doctors_doctor 
            ALTER COLUMN license_number DROP NOT NULL,
            DROP CONSTRAINT IF EXISTS doctors_doctor_license_number_key;
            ''',
            reverse_sql='''
            ALTER TABLE doctors_doctor 
            ALTER COLUMN license_number SET NOT NULL,
            ADD CONSTRAINT doctors_doctor_license_number_key UNIQUE (license_number);
            '''
        ),
    ] 