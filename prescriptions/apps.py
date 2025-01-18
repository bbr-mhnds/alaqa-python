from django.apps import AppConfig

class PrescriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prescriptions'
    verbose_name = 'Prescriptions'

    def ready(self):
        try:
            import prescriptions.signals
        except ImportError:
            pass 