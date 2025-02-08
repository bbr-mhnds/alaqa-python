from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

from .models import Appointment

logger = logging.getLogger(__name__)

class AutoCompleteAppointmentsCronJob(CronJobBase):
    """
    Cron job to automatically mark appointments as complete if they are:
    1. In SCHEDULED state
    2. Their scheduled time has passed by at least 24 hours
    """
    
    # Run every hour
    schedule = Schedule(run_every_mins=60)
    
    code = 'appointments.auto_complete_appointments'  # Unique code
    
    def do(self):
        """Execute the cron job."""
        try:
            # Get the cutoff time (24 hours ago)
            cutoff_time = timezone.now() - timedelta(hours=24)
            
            # Find all appointments that are:
            # - Still in SCHEDULED state
            # - Scheduled more than 24 hours ago
            overdue_appointments = Appointment.objects.filter(
                status='SCHEDULED',
                slot_time__lt=cutoff_time
            )
            
            # Process appointments in batches to avoid memory issues
            batch_size = 100
            total_processed = 0
            total_completed = 0
            
            with transaction.atomic():
                for appointment in overdue_appointments.iterator(chunk_size=batch_size):
                    try:
                        # Update appointment status and add completion time
                        appointment.status = 'COMPLETED'
                        appointment.completion_time = appointment.slot_time + timedelta(hours=1)
                        appointment.notes = f"{appointment.completion_notes or ''}\nAutomatically marked as complete by system on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                        appointment.save()
                        total_completed += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing appointment {appointment.id}: {str(e)}")
                    
                    total_processed += 1
            
            logger.info(f"Auto-completion job finished. Processed {total_processed} appointments, completed {total_completed}.")
            return f"Successfully processed {total_processed} appointments, completed {total_completed}."
            
        except Exception as e:
            error_msg = f"Error in auto-completion cron job: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) 