from io import StringIO
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import cchardet as chardet
from adit.core.forms import DicomNodeChoiceField
from adit.core.models import DicomNode
from adit.core.fields import RestrictedFileField
from adit.core.errors import BatchFileSizeError, BatchFileFormatError
from .models import BatchTransferJob, BatchTransferTask
from .parsers import BatchTransferFileParser


class BatchTransferJobForm(forms.ModelForm):
    source = DicomNodeChoiceField(True, DicomNode.NodeType.SERVER)
    destination = DicomNodeChoiceField(False)
    batch_file = RestrictedFileField(max_upload_size=5242880, label="Batch file")
    ethics_committee_approval = forms.BooleanField()

    class Meta:
        model = BatchTransferJob
        fields = (
            "source",
            "destination",
            "urgent",
            "project_name",
            "project_description",
            "trial_protocol_id",
            "trial_protocol_name",
            "ethics_committee_approval",
            "batch_file",
        )
        labels = {
            "urgent": "Start transfer urgently",
            "trial_protocol_id": "Trial ID",
            "trial_protocol_name": "Trial name",
        }
        help_texts = {
            "urgent": (
                "Start transfer directly (without scheduling) and prioritize it."
            ),
            "trial_protocol_id": (
                "Fill only when to modify the ClinicalTrialProtocolID tag "
                "of all transfered DICOM files. Leave blank otherwise."
            ),
            "trial_protocol_name": (
                "Fill only when to modify the ClinicalTrialProtocolName tag "
                "of all transfered DICOM files. Leave blank otherwise."
            ),
            "batch_file": (
                "The batch file which contains the data to transfer between "
                "two DICOM nodes. See [Help] for how to format this file."
            ),
            "ethics_committee_approval": (
                "Only studies of an approved trial can be transferred!"
                "If unsure contact the support."
            ),
        }

    def __init__(self, *args, **kwargs):
        self.batch_file_errors = None
        self.tasks = None
        self.save_tasks = None

        self.user = kwargs.pop("user")

        super().__init__(*args, **kwargs)

        self.fields["source"].widget.attrs["class"] = "custom-select"
        self.fields["destination"].widget.attrs["class"] = "custom-select"

        if not self.user.has_perm("batch_transfer.can_process_urgently"):
            del self.fields["urgent"]

        self.fields["source"].queryset = self.fields["source"].queryset.order_by(
            "-node_type", "name"
        )
        self.fields["destination"].queryset = self.fields[
            "destination"
        ].queryset.order_by("-node_type", "name")

        self.fields["trial_protocol_id"].widget.attrs["placeholder"] = "Optional"
        self.fields["trial_protocol_name"].widget.attrs["placeholder"] = "Optional"

        self.max_batch_size = (
            settings.MAX_BATCH_TRANSFER_SIZE if not self.user.is_staff else None
        )

        if self.max_batch_size is not None:
            self.fields[
                "batch_file"
            ].help_text = f"Maximum {self.max_batch_size} tasks per transfer job!"

        self.helper = FormHelper(self)
        self.helper.add_input(Submit("save", "Create Job"))

    def clean_ethics_committee_approval(self):
        approval = self.cleaned_data["ethics_committee_approval"]
        if not approval:
            raise ValidationError("Your study must be approved by an ethics committee.")
        return approval

    def clean_batch_file(self):
        batch_file = self.cleaned_data["batch_file"]
        rawdata = batch_file.read()
        encoding = chardet.detect(rawdata)["encoding"]
        file = StringIO(rawdata.decode(encoding))
        can_transfer_unpseudonymized = self.user.has_perm(
            "batch_transfer.can_transfer_unpseudonymized"
        )
        parser = BatchTransferFileParser(
            {
                "task_id": "TaskID",
                "patient_id": "PatientID",
                "study_uid": "StudyInstanceUID",
                "pseudonym": "Pseudonym",
            },
            can_transfer_unpseudonymized,
        )

        try:
            self.tasks = parser.parse(file, self.max_batch_size)

        except BatchFileSizeError as err:
            raise ValidationError(
                f"Too many batch tasks (max. {self.max_batch_size} tasks)"
            ) from err

        except BatchFileFormatError as err:
            self.batch_file_errors = err
            raise ValidationError(
                mark_safe(
                    "Invalid batch file. "
                    '<a href="#" data-toggle="modal" data-target="#batch_file_errors_modal">'
                    "[View details]"
                    "</a>"
                )
            ) from err

        return batch_file

    def _save_tasks(self, batch_job):
        for task in self.tasks:
            task.job = batch_job

        BatchTransferTask.objects.bulk_create(self.tasks)

    def save(self, commit=True):
        with transaction.atomic():
            batch_job = super().save(commit=commit)

            if commit:
                self._save_tasks(batch_job)
            else:
                # If not committing, add a method to the form to allow deferred
                # saving of tasks.
                self.save_tasks = self._save_tasks

        return batch_job
