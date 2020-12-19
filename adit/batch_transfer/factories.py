import factory
from faker import Faker
from adit.core.factories import (
    DicomFolderFactory,
    TransferJobFactory,
    DicomTaskFactory,
    TransferTaskFactory,
)
from .models import BatchTransferJob, BatchTransferRequest, BatchTransferTask

fake = Faker()


class BatchTransferJobFactory(TransferJobFactory):
    class Meta:
        model = BatchTransferJob

    project_name = factory.Faker("sentence")
    project_description = factory.Faker("paragraph")


class BatchTransferJobToPathFactory(BatchTransferJobFactory):
    destination = factory.SubFactory(DicomFolderFactory)


status_codes = [key for key, value in BatchTransferRequest.Status.choices]


class BatchTransferRequestFactory(DicomTaskFactory):
    class Meta:
        model = BatchTransferRequest

    job = factory.SubFactory(BatchTransferJobFactory)
    row_number = factory.Sequence(int)
    patient_id = factory.Faker("numerify", text="##########")
    patient_name = factory.LazyFunction(
        lambda: f"{fake.last_name()}, {fake.first_name()}"
    )
    patient_birth_date = factory.Faker("date_of_birth", minimum_age=15)
    accession_number = factory.Faker("ean")
    study_date = factory.Faker("date_between", start_date="-2y", end_date="today")
    modality = factory.Faker("random_element", elements=("CT", "MR", "DX"))
    pseudonym = factory.Faker(
        "lexify", text="????????", letters="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )


class BatchTransferTaskFactory(TransferTaskFactory):
    class Meta:
        model = BatchTransferTask

    job = factory.SubFactory(BatchTransferJobFactory)
    request = factory.SubFactory(BatchTransferRequestFactory)
