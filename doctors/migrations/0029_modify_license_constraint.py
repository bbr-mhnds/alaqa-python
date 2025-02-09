from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0028_alter_doctor_license_number'),
    ]

    operations = [
        # First drop the existing constraint
        migrations.RunSQL(
            sql='''
            ALTER TABLE doctors_doctor 
            DROP CONSTRAINT IF EXISTS check_license_number_not_empty;
            ''',
            reverse_sql='''
            ALTER TABLE doctors_doctor 
            ADD CONSTRAINT check_license_number_not_empty 
            CHECK (length(trim(license_number)) > 0);
            '''
        ),
        # Add a new constraint that handles NULL values
        migrations.RunSQL(
            sql='''
            ALTER TABLE doctors_doctor 
            ADD CONSTRAINT check_license_number_not_empty 
            CHECK (
                CASE 
                    WHEN license_number IS NULL THEN true
                    ELSE length(trim(license_number)) > 0
                END
            );
            ''',
            reverse_sql='''
            ALTER TABLE doctors_doctor 
            DROP CONSTRAINT IF EXISTS check_license_number_not_empty;
            '''
        ),
        # Update any existing empty strings to NULL
        migrations.RunSQL(
            sql='''
            UPDATE doctors_doctor 
            SET license_number = NULL 
            WHERE license_number = '' OR length(trim(license_number)) = 0;
            ''',
            reverse_sql=''
        ),
    ] 