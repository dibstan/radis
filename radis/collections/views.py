from typing import Any, Protocol, cast, runtime_checkable

from adit_radis_shared.common.mixins import PageSizeSelectMixin
from adit_radis_shared.common.types import AuthenticatedHttpRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import SuspiciousOperation
from django.db import IntegrityError
from django.db.models import Count, QuerySet
from django.forms import BaseModelForm, modelform_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin
from django_htmx.http import HttpResponseClientRefresh, trigger_client_event
from django_tables2 import SingleTableView

from radis.reports.models import Report

from .filters import CollectionFilter
from .models import Collection
from .tables import CollectionTable

LAST_USED_COLLECTION_PREFERENCE = "last_used_collection"


@runtime_checkable
class AnnotatedCollection(Protocol):
    has_report: bool


class CollectionListView(LoginRequiredMixin, SingleTableView):
    request: AuthenticatedHttpRequest
    model = Collection
    table_class = CollectionTable
    filterset_class = CollectionFilter
    paginate_by = 30

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["collections/_collection_list.html"]
        return ["collections/collection_list.html"]

    def get_queryset(self) -> QuerySet[Collection]:
        return (
            Collection.objects.filter(owner=self.request.user)
            .prefetch_related("reports")
            .annotate(num_reports=Count("reports"))
        )


class CollectionCreateView(
    LoginRequiredMixin,
    CreateView,
):
    model = Collection
    template_name = "collections/_collection_create.html"
    form_class = modelform_factory(Collection, fields=["name"])

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.owner = self.request.user
        try:
            self.object = form.save()
        except IntegrityError as err:
            if "unique_collection_name_per_user" in str(err):
                form.add_error("name", "A collection with this name already exists.")
                return self.form_invalid(form)
            raise err

        response = HttpResponse(status=204)
        return trigger_client_event(response, "collectionListChanged")


class CollectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Collection
    template_name = "collections/_collection_update.html"
    form_class = modelform_factory(Collection, fields=["name"])

    def get_queryset(self) -> QuerySet[Collection]:
        return super().get_queryset().filter(owner=self.request.user)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.owner = self.request.user
        try:
            self.object = form.save()
        except IntegrityError as err:
            if "unique_collection_name_per_user" in str(err):
                form.add_error("name", "A collection with this name already exists.")
                return self.form_invalid(form)
            raise err

        return HttpResponseClientRefresh()


class CollectionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Collection
    success_url = reverse_lazy("collection_list")
    success_message = "Collection successfully deleted"

    def get_queryset(self) -> QuerySet[Collection]:
        return super().get_queryset().filter(owner=self.request.user)


class CollectionDetailView(
    LoginRequiredMixin,
    PageSizeSelectMixin,
    SingleObjectMixin,
    ListView,
):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        self.object = self.get_object(queryset=Collection.objects.filter(owner=self.request.user))
        return super().get(request)

    def get_template_names(self) -> list[str]:
        request = cast(AuthenticatedHttpRequest, self.request)
        if request.htmx:
            return ["collections/_collection_detail.html"]
        return ["collections/collection_detail.html"]

    def get_queryset(self) -> QuerySet[Report]:
        return cast(Collection, self.object).reports.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["collection"] = context["object"]
        context["reports"] = context["object_list"]
        return context


class CollectionSelectView(LoginRequiredMixin, View):
    def get(self, request: AuthenticatedHttpRequest, report_id: int) -> HttpResponse:
        addable_collections: list[Collection] = []
        removable_collections: list[Collection] = []
        collections = (
            Collection.objects.get_queryset().filter(owner=request.user).with_has_report(report_id)
        )
        for collection in collections:
            assert isinstance(collection, AnnotatedCollection)
            if collection.has_report:
                removable_collections.append(collection)
            else:
                addable_collections.append(collection)

        last_used_collection = request.user.preferences.get(LAST_USED_COLLECTION_PREFERENCE)

        return render(
            request,
            "collections/_collection_select.html",
            {
                "report_id": report_id,
                "addable_collections": addable_collections,
                "removable_collections": removable_collections,
                "last_used_collection": last_used_collection,
            },
        )

    def post(self, request: AuthenticatedHttpRequest, report_id: int) -> HttpResponse:
        # user_id = request.user.id
        action = request.POST.get("action")
        collection_id = request.POST.get("collection")

        collection = get_object_or_404(
            Collection.objects.filter(owner=request.user), pk=collection_id
        )
        report = get_object_or_404(Report, id=report_id)

        response = HttpResponse(status=200)
        if action == "add":
            if collection.reports.contains(report):
                raise SuspiciousOperation

            collection.reports.add(report)
            request.user.preferences[LAST_USED_COLLECTION_PREFERENCE] = collection.id
            request.user.save()
            response = trigger_client_event(response, f"collectedReportsChanged_{collection.id}")
            response = trigger_client_event(response, f"collectionsOfReportChanged_{report_id}")
        elif action == "remove":
            if not collection.reports.contains(report):
                raise SuspiciousOperation

            collection.reports.remove(report)
            response = trigger_client_event(response, f"collectedReportsChanged_{collection.id}")
            response = trigger_client_event(response, f"collectionsOfReportChanged_{report_id}")
        else:
            raise SuspiciousOperation(f"Invalid action: {action}")

        return response


class CollectionCountBadgeView(LoginRequiredMixin, View):
    def get(self, request: AuthenticatedHttpRequest, report_id: int) -> HttpResponse:
        report = get_object_or_404(Report, id=report_id)
        collection_count = Collection.objects.filter(
            owner=request.user, reports__id=report.id
        ).count()
        return render(
            request,
            "collections/_collection_count_badge.html",
            {"report": report, "collection_count": collection_count},
        )


class CollectedReportRemoveView(LoginRequiredMixin, View):
    def post(self, request: AuthenticatedHttpRequest, pk: int, report_id: int) -> HttpResponse:
        collection = get_object_or_404(Collection.objects.filter(owner=request.user), pk=pk)
        report = get_object_or_404(Report, id=report_id)

        if not collection.reports.contains(report):
            raise SuspiciousOperation

        collection.reports.remove(report)

        return HttpResponseClientRefresh()
