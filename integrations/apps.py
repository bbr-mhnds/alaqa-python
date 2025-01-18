from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations'
    verbose_name = _('Integrations')
    
    def ready(self):
        """
        Initialize app when it's ready.
        Import signals here to avoid circular imports.
        """
        try:
            # Import signals
            from . import signals
        except ImportError:
            pass
