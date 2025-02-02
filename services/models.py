from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

class Service(models.Model):
    name_en = models.CharField(_('Name (English)'), max_length=255)
    name_ar = models.CharField(_('Name (Arabic)'), max_length=255)
    description_en = models.TextField(_('Description (English)'))
    description_ar = models.TextField(_('Description (Arabic)'))
    icon = models.ImageField(
        _('Icon'),
        upload_to='services/icons/',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg'])]
    )
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        ordering = ['-created_at']

    def __str__(self):
        return self.name_en
