from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0016_fix_doctor_verification_schema'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP TABLE IF EXISTS doctors_doctorverification;
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
            """,
            # Reverse SQL - recreate the table with original schema if needed
            """
            DROP TABLE IF EXISTS doctors_doctorverification;
            CREATE TABLE doctors_doctorverification (
                id SERIAL PRIMARY KEY,
                email VARCHAR(254) NOT NULL,
                phone VARCHAR(17) NOT NULL,
                email_verified BOOLEAN NOT NULL DEFAULT FALSE,
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