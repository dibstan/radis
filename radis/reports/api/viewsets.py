from typing import Any

from django.db import transaction
from django.http import Http404
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request, clone_request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from radis.reports.tasks import report_created, report_deleted, report_updated

from ..models import Report
from ..site import document_fetchers
from .serializers import ReportSerializer


class ReportViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet for fetch, creating, updating, and deleting Reports.

    Only admins (staff users) can do that.
    """

    serializer_class = ReportSerializer
    queryset = Report.objects.all()
    lookup_field = "document_id"
    permission_classes = [IsAdminUser]

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Retrieve a single Report.

        It also fetches the associated document from the Vespa database.
        """
        full = request.GET.get("full", "").lower() in ["true", "1", "yes"]

        instance: Report = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        if full:
            documents = {}
            for fetcher in document_fetchers.values():
                document = fetcher.fetch(instance)
                if document:
                    documents[fetcher.source] = document
            data["documents"] = documents

        return Response(data)

    def perform_create(self, serializer: BaseSerializer) -> None:
        super().perform_create(serializer)
        assert serializer.instance
        report: Report = serializer.instance
        transaction.on_commit(lambda: report_created.delay(report.document_id))

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # DRF itself does not support upsert (create the object to update if it does not exist).
        # This workaround is inspired by https://gist.github.com/tomchristie/a2ace4577eff2c603b1b
        upsert = request.GET.get("upsert", "").lower() in ["true", "1", "yes"]
        if not upsert:
            return super().update(request, *args, **kwargs)
        else:
            instance = self.get_object_or_none()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            if instance is None:
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            self.perform_update(serializer)
            return Response(serializer.data)

    def get_object_or_none(self) -> Report | None:
        try:
            return self.get_object()
        except Http404:
            if self.request.method == "PUT":
                self.check_permissions(clone_request(self.request, "POST"))
            else:
                raise

    def perform_update(self, serializer: BaseSerializer) -> None:
        super().perform_update(serializer)
        assert serializer.instance
        report: Report = serializer.instance
        transaction.on_commit(lambda: report_updated.delay(report.document_id))

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert request.method
        raise MethodNotAllowed(request.method)

    def perform_destroy(self, instance: Report) -> None:
        super().perform_destroy(instance)
        transaction.on_commit(lambda: report_deleted.delay(instance.document_id))
