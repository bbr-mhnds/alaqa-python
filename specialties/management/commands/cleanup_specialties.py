from django.core.management.base import BaseCommand
from specialties.models import Specialty
from django.db.models import Count

class Command(BaseCommand):
    help = 'Clean up duplicate specialties'

    def handle(self, *args, **kwargs):
        # Find duplicates based on title
        duplicates = (
            Specialty.objects.values('title')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        self.stdout.write(f"Found {len(duplicates)} duplicate specialty titles")

        for duplicate in duplicates:
            title = duplicate['title']
            specialties = Specialty.objects.filter(title=title).order_by('created_at')
            
            # Keep the first one (oldest) and delete the rest
            keep = specialties.first()
            to_delete = specialties.exclude(id=keep.id)
            
            self.stdout.write(f"For title '{title}':")
            self.stdout.write(f"- Keeping: {keep.id} (created at {keep.created_at})")
            self.stdout.write(f"- Deleting {to_delete.count()} duplicates")
            
            to_delete.delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleaned up duplicate specialties')) 