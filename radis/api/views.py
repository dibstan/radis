from typing import Any

from rest_framework import mixins, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from radis.reports.models import Report

from .serializers import ReportSerializer
from .site import document_fetchers, report_event_handlers


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
        instance: Report = self.get_object()

        extra = {}
        for fetcher in document_fetchers:
            document = fetcher.fetch(instance)
            if document:
                extra[fetcher.source] = document

        serializer = self.get_serializer(instance)
        data = serializer.data
        data.update(extra)

        return Response(data)

    def perform_create(self, serializer: BaseSerializer) -> None:
        super().perform_create(serializer)
        assert serializer.instance
        report: Report = serializer.instance
        for handler in report_event_handlers:
            handler("created", report)

    def perform_update(self, serializer: BaseSerializer) -> None:
        super().perform_update(serializer)
        assert serializer.instance
        report: Report = serializer.instance
        for handler in report_event_handlers:
            handler("updated", report)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert request.method
        raise MethodNotAllowed(request.method)

    def perform_destroy(self, instance: Report) -> None:
        super().perform_destroy(instance)
        for handler in report_event_handlers:
            handler("deleted", instance)
