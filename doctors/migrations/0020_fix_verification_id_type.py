from django.db import migrations
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0019_reset_verification_table'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Change id to UUID
            """
            DROP TABLE IF EXISTS doctors_doctorverification CASCADE;
            CREATE TABLE doctors_doctorverification (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(254) NOT NULL,
                phone VARCHAR(17) NOT NULL,
                email_verified BOOLEAN NOT NULL DEFAULT TRUE,
                phone_verified BOOLEAN NOT NULL DEFAULT FALSE,
                registration_data JSONB DEFAULT '{}',
                license_document VARCHAR(100) NULL,
                qualification_document VARCHAR(100) NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                is_used BOOLEAN NOT NULL DEFAULT FALSE
            );
            """,
            # Reverse SQL - Change back to SERIAL if needed
            """
            DROP TABLE IF EXISTS doctors_doctorverification CASCADE;
            CREATE TABLE doctors_doctorverification (
                id SERIAL PRIMARY KEY,
                email VARCHAR(254) NOT NULL,
                phone VARCHAR(17) NOT NULL,
                email_verified BOOLEAN NOT NULL DEFAULT TRUE,
                phone_verified BOOLEAN NOT NULL DEFAULT FALSE,
                registration_data JSONB DEFAULT '{}',
                license_document VARCHAR(100) NULL,
                qualification_document VARCHAR(100) NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                is_used BOOLEAN NOT NULL DEFAULT FALSE
            );
            """
        ),
    ] 