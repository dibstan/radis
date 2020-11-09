from django.urls import path
from django.views.generic import TemplateView
from .views import (
    TransferJobListView,
    TransferJobListAPIView,
    redirect_to_job_detail_view,
    TransferJobDeleteView,
    TransferJobCancelView,
    TransferJobVerifyView,
    FlowerProxyView,
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="core/home.html"), name="home"),
    path("transfer-jobs/", TransferJobListView.as_view(), name="transfer_job_list"),
    path(
        "api/transfer-jobs/",
        TransferJobListAPIView.as_view(),
    ),
    path(
        "transfer-jobs/<int:pk>/",
        redirect_to_job_detail_view,
        name="transfer_job_detail",
    ),
    path(
        "transfer-jobs/<int:pk>/delete/",
        TransferJobDeleteView.as_view(),
        name="transfer_job_delete",
    ),
    path(
        "transfer-jobs/<int:pk>/cancel/",
        TransferJobCancelView.as_view(),
        name="transfer_job_cancel",
    ),
    path(
        "transfer-jobs/<int:pk>/verify/",
        TransferJobVerifyView.as_view(),
        name="transfer_job_verify",
    ),
    FlowerProxyView.as_url(),
]