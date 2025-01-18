import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class DrugCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=255)
    name_arabic = models.CharField(_("Arabic Name"), max_length=255)
    status = models.BooleanField(_("Status"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Drug Category")
        verbose_name_plural = _("Drug Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name


class DrugDosageForm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=255)
    name_arabic = models.CharField(_("Arabic Name"), max_length=255)
    status = models.BooleanField(_("Status"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Drug Dosage Form")
        verbose_name_plural = _("Drug Dosage Forms")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Drug(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=255)
    name_arabic = models.CharField(_("Arabic Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    description_arabic = models.TextField(_("Arabic Description"), blank=True)
    category = models.ForeignKey(
        DrugCategory,
        verbose_name=_("Category"),
        on_delete=models.PROTECT,
        related_name="drugs"
    )
    dosage_form = models.ForeignKey(
        DrugDosageForm,
        verbose_name=_("Dosage Form"),
        on_delete=models.PROTECT,
        related_name="drugs"
    )
    strength = models.CharField(_("Strength"), max_length=100)
    manufacturer = models.CharField(_("Manufacturer"), max_length=255)
    status = models.BooleanField(_("Status"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Drug")
        verbose_name_plural = _("Drugs")
        ordering = ["name"]

    def __str__(self):
        return self.name
