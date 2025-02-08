from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0024_merge_20250208_2238'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Recreate table with all required fields
            """
            DROP TABLE IF EXISTS doctors_doctorverification CASCADE;
            CREATE TABLE doctors_doctorverification (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(254) NOT NULL,
                phone VARCHAR(17) NOT NULL,
                email_code VARCHAR(6) DEFAULT '000000',
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
            # Reverse SQL - Revert changes if needed
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
            """
        ),
    ] 