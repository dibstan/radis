from datetime import timezone
from typing import Generic, TypeVar

import factory
from faker import Faker

from .models import Metadata, Modality, Report

T = TypeVar("T")

fake = Faker()

MODALITIES = ("CT", "MR", "DX", "PT", "US")


class BaseDjangoModelFactory(Generic[T], factory.django.DjangoModelFactory):
    @classmethod
    def create(cls, *args, **kwargs) -> T:
        return super().create(*args, **kwargs)


class ModalityFactory(BaseDjangoModelFactory[Modality]):
    class Meta:
        model = Modality
        django_get_or_create = ("code",)

    code = factory.Faker("random_element", elements=MODALITIES)


class MetadataFactory(BaseDjangoModelFactory[Metadata]):
    class Meta:
        model = Metadata

    key = factory.Sequence(lambda n: f"{fake.word()}_{n}")
    value = factory.Faker("word")


class ReportFactory(BaseDjangoModelFactory[Report]):
    class Meta:
        model = Report

    document_id = factory.Faker("uuid4")
    language = "en"
    pacs_aet = factory.Faker("word")
    pacs_name = factory.Faker("word")
    patient_id = factory.Faker("numerify", text="##########")
    patient_birth_date = factory.Faker("date_of_birth", minimum_age=15)
    patient_sex = factory.Faker("random_element", elements=["M", "F", "O"])
    study_description = factory.Faker("text", max_nb_chars=64)
    study_datetime = factory.Faker("date_time_between", start_date="-10y", tzinfo=timezone.utc)
    links = factory.LazyFunction(lambda: [fake.url() for _ in range(fake.random_int(1, 3))])
    metadata = factory.RelatedFactoryList(
        MetadataFactory,
        factory_related_name="report",
        size=lambda: fake.random_int(1, 5),  # type: ignore
    )
    body = factory.Faker("paragraph")

    @factory.post_generation
    def modalities(self, create, extracted, **kwargs):
        """
        If called like: ReportFactory.create(modalities=["CT", "PT"]) it generates
        a report with 2 modalities. If called without `modalities` argument, it
        generates a random amount of modalities for the report.
        """
        if not create:
            return

        modalities = extracted
        if modalities is None:
            modalities = fake.random_elements(elements=MODALITIES, unique=True)

        for modality in modalities:
            # We can't call the create method of the factory as
            # django_get_or_create would not be respected then
            self.modalities.add(ModalityFactory(code=modality))  # type: ignore
