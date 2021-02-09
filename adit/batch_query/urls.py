from django.urls import path
from .views import (
    BatchQueryJobListView,
    BatchQueryJobCreateView,
    BatchQueryJobDetailView,
    BatchQueryJobDeleteView,
    BatchQueryJobVerifyView,
    BatchQueryJobCancelView,
    BatchQueryJobResumeView,
    BatchQueryJobRetryView,
    BatchQueryTaskDetailView,
    BatchQueryResultListView,
    BatchQueryResultDownloadView,
)


urlpatterns = [
    path(
        "jobs/",
        BatchQueryJobListView.as_view(),
        name="batch_query_job_list",
    ),
    path(
        "jobs/new/",
        BatchQueryJobCreateView.as_view(),
        name="batch_query_job_create",
    ),
    path(
        "jobs/<int:pk>/",
        BatchQueryJobDetailView.as_view(),
        name="batch_query_job_detail",
    ),
    path(
        "jobs/<int:pk>/delete/",
        BatchQueryJobDeleteView.as_view(),
        name="batch_query_job_delete",
    ),
    path(
        "jobs/<int:pk>/verify/",
        BatchQueryJobVerifyView.as_view(),
        name="batch_query_job_verify",
    ),
    path(
        "jobs/<int:pk>/cancel/",
        BatchQueryJobCancelView.as_view(),
        name="batch_query_job_cancel",
    ),
    path(
        "jobs/<int:pk>/resume/",
        BatchQueryJobResumeView.as_view(),
        name="batch_query_job_resume",
    ),
    path(
        "jobs/<int:pk>/retry/",
        BatchQueryJobRetryView.as_view(),
        name="batch_query_job_retry",
    ),
    path(
        "jobs/<int:pk>/results/",
        BatchQueryResultListView.as_view(),
        name="batch_query_result_list",
    ),
    path(
        "jobs/<int:pk>/download/",
        BatchQueryResultDownloadView.as_view(),
        name="batch_query_result_download",
    ),
    path(
        "jobs/<int:job_id>/tasks/<int:task_id>/",
        BatchQueryTaskDetailView.as_view(),
        name="batch_query_task_detail",
    ),
]
