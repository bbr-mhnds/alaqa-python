from django.db import migrations

class Migration(migrations.Migration):
    atomic = True
    
    dependencies = [
        ('doctors', '0025_add_verification_fields'),
    ]

    operations = [
        # First drop the unique constraint
        migrations.RunSQL(
            sql='ALTER TABLE doctors_doctor DROP CONSTRAINT doctors_doctor_license_number_key;',
            reverse_sql='ALTER TABLE doctors_doctor ADD CONSTRAINT doctors_doctor_license_number_key UNIQUE (license_number);'
        ),
        # Update empty license numbers
        migrations.RunSQL(
            sql='''
            UPDATE doctors_doctor 
            SET license_number = CONCAT('TEMP-', id::text) 
            WHERE license_number = '';
            ''',
            reverse_sql=''
        ),
        # Add back the unique constraint
        migrations.RunSQL(
            sql='ALTER TABLE doctors_doctor ADD CONSTRAINT doctors_doctor_license_number_key UNIQUE (license_number);',
            reverse_sql='ALTER TABLE doctors_doctor DROP CONSTRAINT doctors_doctor_license_number_key;'
        ),
    ] 