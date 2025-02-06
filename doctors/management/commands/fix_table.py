from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix the doctor verification table using Django ORM'

    def handle(self, *args, **options):
        # Drop and recreate the table
        with connection.cursor() as cursor:
            # Drop the table
            cursor.execute("""
                DROP TABLE IF EXISTS doctors_doctorverification CASCADE;
            """)
            
            # Create the table with the correct schema
            cursor.execute("""
                CREATE TABLE doctors_doctorverification (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(254) NOT NULL,
                    phone VARCHAR(17) NOT NULL,
                    email_code VARCHAR(6) NOT NULL DEFAULT '000000',
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
            
            self.stdout.write(self.style.SUCCESS('Successfully recreated the verification table')) 