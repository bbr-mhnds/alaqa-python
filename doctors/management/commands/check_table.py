from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check the doctor verification table structure'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'doctors_doctorverification'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            self.stdout.write("Table structure:")
            for col in columns:
                self.stdout.write(f"- {col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else "")) 