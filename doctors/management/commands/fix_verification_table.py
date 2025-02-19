from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix the doctor verification table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Drop the existing table
            cursor.execute("DROP TABLE IF EXISTS doctors_doctorverification CASCADE;")
            
            # Create the table with correct schema
            cursor.execute("""
                CREATE TABLE doctors_doctorverification (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(254) NOT NULL,
                    phone VARCHAR(17) NOT NULL,
                    email_code VARCHAR(6) NOT NULL DEFAULT '000000',
                    sms_code VARCHAR(6) NOT NULL DEFAULT '000000',
                    email_verified BOOLEAN NOT NULL DEFAULT TRUE,
                    phone_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    registration_data JSONB DEFAULT '{}',
                    license_document VARCHAR(100) NULL,
                    qualification_document VARCHAR(100) NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_used BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)
            
            # Mark all migrations as applied
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                SELECT 'doctors', unnest(ARRAY[
                    '0015_fix_verification_fields',
                    '0016_fix_doctor_verification_schema',
                    '0017_recreate_doctor_verification',
                    '0018_fix_verification_table',
                    '0019_reset_verification_table',
                    '0020_merge_20250206_1339',
                    '0021_add_email_code_field'
                ]), NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app = 'doctors' AND name = ANY(ARRAY[
                        '0015_fix_verification_fields',
                        '0016_fix_doctor_verification_schema',
                        '0017_recreate_doctor_verification',
                        '0018_fix_verification_table',
                        '0019_reset_verification_table',
                        '0020_merge_20250206_1339',
                        '0021_add_email_code_field'
                    ])
                );
            """)
            
            self.stdout.write(self.style.SUCCESS('Successfully fixed verification table')) 