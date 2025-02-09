from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0030_alter_doctor_license_number_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop all constraints related to license_number
            sql='''
            ALTER TABLE doctors_doctor 
            DROP CONSTRAINT IF EXISTS check_license_number_not_empty,
            DROP CONSTRAINT IF EXISTS doctors_doctor_license_number_key;
            
            ALTER TABLE doctors_doctor 
            ALTER COLUMN license_number DROP NOT NULL;
            ''',
            reverse_sql='''
            ALTER TABLE doctors_doctor 
            ADD CONSTRAINT doctors_doctor_license_number_key UNIQUE (license_number);
            '''
        ),
    ] 