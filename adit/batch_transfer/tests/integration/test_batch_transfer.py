import pytest
from playwright.sync_api import Page, expect

from adit.batch_transfer.models import BatchTransferJob


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_unpseudonymized_urgent_batch_transfer_succeeds(
    page: Page,
    setup_orthancs,
    adit_celery_worker,
    channels_liver_server,
    create_and_login_user,
    create_csv_file,
):
    batch_file = create_csv_file(
        [
            ["PatientID", "StudyInstanceUID"],
            ["1005", "1.2.840.113845.11.1000000001951524609.20200705173311.2689472"],
        ]
    )

    user = create_and_login_user(channels_liver_server.url)
    user.join_group("batch_transfer_group")
    user.add_permission("can_process_urgently", BatchTransferJob)
    user.add_permission("can_transfer_unpseudonymized", BatchTransferJob)

    page.goto(channels_liver_server.url + "/batch-transfer/jobs/new/")
    page.get_by_label("Source").select_option(label="DICOM Server Orthanc Test Server 1")
    page.get_by_label("Destination").select_option(label="DICOM Server Orthanc Test Server 2")
    page.get_by_label("Start transfer urgently").click(force=True)
    page.get_by_label("Project name").fill("Test transfer")
    page.get_by_label("Project description").fill("Just a test transfer.")
    page.get_by_label("Ethics committee approval").fill("I have it, I swear.")
    page.get_by_label("Batch file").set_input_files(files=[batch_file])
    page.locator('input:has-text("Create job")').click()
    expect(page.locator('dl:has-text("Success")').poll()).to_be_visible()
    page.screenshot(path="foo.png")