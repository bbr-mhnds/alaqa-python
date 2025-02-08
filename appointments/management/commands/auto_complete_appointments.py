from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from appointments.models import Appointment
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Automatically completes appointments that are past their scheduled time and still in SCHEDULED state'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours after scheduled time to wait before auto-completing (default: 24)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of appointments to process in each batch (default: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making actual changes'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        # Calculate the cutoff time
        cutoff_time = timezone.now() - timezone.timedelta(hours=hours)
        
        # Find appointments that are past their scheduled time and still in SCHEDULED state
        overdue_appointments = Appointment.objects.filter(
            status='SCHEDULED',
            slot_time__lt=cutoff_time
        ).select_related('doctor')  # Optimize by pre-fetching doctor data
        
        total_count = overdue_appointments.count()
        
        if dry_run:
            self.stdout.write(f"Found {total_count} overdue appointments that would be auto-completed")
            for appointment in overdue_appointments:
                self.stdout.write(
                    f"Would auto-complete appointment {appointment.id} "
                    f"for doctor {appointment.doctor.email} "
                    f"scheduled for {appointment.slot_time}"
                )
            return

        completed_count = 0
        error_count = 0
        processed_count = 0

        # Process appointments in batches to avoid memory issues
        while processed_count < total_count:
            batch = overdue_appointments[processed_count:processed_count + batch_size]
            
            for appointment in batch:
                try:
                    with transaction.atomic():
                        # Calculate a reasonable completion time (30 minutes after scheduled time)
                        completion_time = min(
                            appointment.slot_time + timezone.timedelta(minutes=30),
                            timezone.now()
                        )
                        
                        # Update the appointment
                        appointment.status = 'COMPLETED'
                        appointment.completion_time = completion_time
                        appointment.completion_notes = (
                            "This appointment was automatically marked as completed by the system.\n"
                            f"Original scheduled time: {appointment.slot_time}\n"
                            f"Auto-completed on: {timezone.now()}\n"
                            "Reason: No manual completion after scheduled time (24+ hours overdue)."
                        )
                        appointment.duration_minutes = 30  # Default duration
                        appointment.save()
                        
                        logger.info(
                            f"Auto-completed appointment {appointment.id} "
                            f"for doctor {appointment.doctor.email} "
                            f"scheduled at {appointment.slot_time}"
                        )
                        completed_count += 1
                        
                except Exception as e:
                    error_message = (
                        f"Failed to auto-complete appointment {appointment.id}: {str(e)}\n"
                        f"Doctor: {appointment.doctor.email}\n"
                        f"Scheduled time: {appointment.slot_time}"
                    )
                    logger.error(error_message)
                    error_count += 1
            
            processed_count += len(batch)
            # Print progress
            self.stdout.write(
                f"Processed {processed_count}/{total_count} appointments. "
                f"Completed: {completed_count}, Errors: {error_count}"
            )

        # Print final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"Auto-completion finished.\n"
                f"Total appointments processed: {total_count}\n"
                f"Successfully completed: {completed_count}\n"
                f"Errors encountered: {error_count}"
            )
        ) 