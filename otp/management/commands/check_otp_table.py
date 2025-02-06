from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check the OTP table structure'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'otp_otp'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            self.stdout.write("OTP Table structure:")
            for col in columns:
                self.stdout.write(f"- {col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else ""))
                
            # Also check for any recent OTP records
            cursor.execute("""
                SELECT id, phone_number, otp_code, is_verified, attempts, expires_at, created_at
                FROM otp_otp
                ORDER BY created_at DESC
                LIMIT 5;
            """)
            records = cursor.fetchall()
            
            if records:
                self.stdout.write("\nRecent OTP records:")
                for record in records:
                    self.stdout.write(f"- ID: {record[0]}, Phone: {record[1]}, Code: {record[2]}, Verified: {record[3]}, Attempts: {record[4]}, Expires: {record[5]}, Created: {record[6]}") 