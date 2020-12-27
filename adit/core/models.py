from datetime import time
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from .utils.dicom_connector import DicomConnector
from .validators import (
    no_backslash_char_validator,
    no_control_chars_validator,
    no_wildcard_chars_validator,
    validate_uid_list,
)


class CoreSettings(models.Model):
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Core settings"

    @classmethod
    def get(cls):
        return cls.objects.first()


def slot_time(hour, minute):
    return time(hour, minute)


class AppSettings(models.Model):
    # Lock the creation of new jobs
    locked = models.BooleanField(default=False)
    # Suspend the background processing.
    suspended = models.BooleanField(default=False)
    # Must be set in UTC time as Celery workers can't figure out another time zone.
    slot_begin_time = models.TimeField(
        default=slot_time(22, 0),
        help_text=f"Must be set in {settings.TIME_ZONE} time zone.",
    )
    # Must be set in UTC time as Celery workers can't figure out another time zone.
    slot_end_time = models.TimeField(
        default=slot_time(8, 0),
        help_text=f"Must be set in {settings.TIME_ZONE} time zone.",
    )
    # Timeout between transfer tasks
    transfer_timeout = models.IntegerField(default=3)

    class Meta:
        abstract = True

    @classmethod
    def get(cls):
        return cls.objects.first()


class DicomNode(models.Model):
    NODE_TYPE = None

    class NodeType(models.TextChoices):
        SERVER = "SV", "Server"
        FOLDER = "FO", "Folder"

    class Meta:
        ordering = ("name",)

    node_type = models.CharField(max_length=2, choices=NodeType.choices)
    name = models.CharField(unique=True, max_length=64)
    source_active = models.BooleanField(default=True)
    destination_active = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.node_type:
            if not self.NODE_TYPE in dict(self.NodeType.choices):
                raise AssertionError(f"Invalid node type: {self.NODE_TYPE}")
            self.node_type = self.NODE_TYPE

    def __str__(self):
        node_types_dict = dict(self.NodeType.choices)
        return f"DICOM {node_types_dict[self.node_type]} {self.name}"


class DicomServer(DicomNode):
    NODE_TYPE = DicomNode.NodeType.SERVER

    ae_title = models.CharField(unique=True, max_length=16)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(65535)]
    )
    patient_root_find_support = models.BooleanField(default=True)
    patient_root_get_support = models.BooleanField(default=True)
    patient_root_move_support = models.BooleanField(default=True)
    study_root_find_support = models.BooleanField(default=True)
    study_root_get_support = models.BooleanField(default=True)
    study_root_move_support = models.BooleanField(default=True)

    def create_connector(self, auto_connect=True):
        return DicomConnector(
            DicomConnector.Config(
                client_ae_title=settings.ADIT_AE_TITLE,
                server_ae_title=self.ae_title,
                server_host=self.host,
                server_port=self.port,
                rabbitmq_url=settings.RABBITMQ_URL,
                patient_root_find_support=self.patient_root_find_support,
                patient_root_get_support=self.patient_root_get_support,
                patient_root_move_support=self.patient_root_move_support,
                study_root_find_support=self.study_root_find_support,
                study_root_get_support=self.study_root_get_support,
                study_root_move_support=self.study_root_move_support,
                auto_connect=auto_connect,
            )
        )


class DicomFolder(DicomNode):
    NODE_TYPE = DicomNode.NodeType.FOLDER

    path = models.CharField(max_length=256)
    quota = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="The disk quota of this folder in MB.",
    )
    warn_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="When to warn the admins by Email (used space in MB).",
    )


class DicomJob(models.Model):
    class Status(models.TextChoices):
        UNVERIFIED = "UV", "Unverified"
        PENDING = "PE", "Pending"
        IN_PROGRESS = "IP", "In Progress"
        CANCELING = "CI", "Canceling"
        CANCELED = "CA", "Canceled"
        SUCCESS = "SU", "Success"
        WARNING = "WA", "Warning"
        FAILURE = "FA", "Failure"

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["owner", "status"])]
        permissions = [
            (
                "can_process_urgently",
                "Can process urgently (prioritized and without scheduling).",
            )
        ]

    source = models.ForeignKey(DicomNode, related_name="+", on_delete=models.PROTECT)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.UNVERIFIED
    )
    urgent = models.BooleanField(default=False)
    message = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_jobs",
    )
    created = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def is_deletable(self):
        return self.status in (self.Status.UNVERIFIED, self.Status.PENDING)

    def is_cancelable(self):
        return self.status in (self.Status.IN_PROGRESS,)

    def is_verified(self):
        return self.status != self.Status.UNVERIFIED

    def __str__(self):
        return f"{self.__class__.__name__} [ID {self.id}]"


class TransferJob(DicomJob):
    class Meta(DicomJob.Meta):
        abstract = True

    destination = models.ForeignKey(
        DicomNode, related_name="+", on_delete=models.PROTECT
    )
    trial_protocol_id = models.CharField(
        blank=True, max_length=64, validators=[no_backslash_char_validator]
    )
    trial_protocol_name = models.CharField(
        blank=True, max_length=64, validators=[no_backslash_char_validator]
    )
    archive_password = models.CharField(blank=True, max_length=50)

    def get_processed_tasks(self):
        non_processed = (TransferTask.Status.PENDING, TransferTask.Status.IN_PROGRESS)
        return self.tasks.exclude(status__in=non_processed)


class DicomTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "PE", "Pending"
        IN_PROGRESS = "IP", "In Progress"
        CANCELED = "CA", "Canceled"
        SUCCESS = "SU", "Success"
        WARNING = "WA", "Warning"
        FAILURE = "FA", "Failure"

    class Meta:
        abstract = True
        ordering = ("id",)

    job = None
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PENDING,
    )
    message = models.TextField(blank=True, default="")
    log = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.__class__.__name__} [Task ID {self.id}, Job ID {self.job.id}]"


class TransferTask(DicomTask):
    class Meta(DicomTask.Meta):
        abstract = True

    patient_id = models.CharField(
        blank=True,
        max_length=64,
        validators=[
            no_backslash_char_validator,
            no_control_chars_validator,
            no_wildcard_chars_validator,
        ],
    )
    accession_number = models.CharField(
        blank=True,
        max_length=16,
        validators=[
            no_backslash_char_validator,
            no_control_chars_validator,
            no_wildcard_chars_validator,
        ],
    )
    study_uid = models.CharField(
        blank=True,
        max_length=64,
        validators=[
            no_backslash_char_validator,
            no_control_chars_validator,
            no_wildcard_chars_validator,
        ],
    )
    series_uids = models.JSONField(
        null=True,
        blank=True,
        validators=[validate_uid_list],
    )
    pseudonym = models.CharField(
        blank=True,
        max_length=64,
        validators=[no_backslash_char_validator, no_control_chars_validator],
    )

    def clean(self):
        if not (self.accession_number or self.study_uid):
            raise ValidationError(
                "A study must be identifiable by either an 'Accession Number' "
                "or a 'Study Instance UID'."
            )

    def __str__(self):
        return (
            f"{self.__class__.__name__} "
            f"[Source {self.job.source.name}, "
            f"Destination {self.job.destination}, "
            f"Task ID {self.id}, Job ID {self.job.id}]"
        )
