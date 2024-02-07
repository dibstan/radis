import json
from os import environ
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from faker import Faker

from radis.accounts.factories import AdminUserFactory, GroupFactory, UserFactory
from radis.accounts.models import User
from radis.reports.factories import ReportFactory
from radis.reports.models import Report
from radis.reports.site import report_event_handlers
from radis.token_authentication.factories import TokenFactory
from radis.token_authentication.models import FRACTION_LENGTH
from radis.token_authentication.utils.crypto import hash_token

USER_COUNT = 20
GROUP_COUNT = 3
ADMIN_AUTH_TOKEN = "f2e7412ca332a85e37f3fce88c6a1904fe35ad63"
PACS_ITEMS = [
    {"pacs_aet": "gepacs", "pacs_name": "GE PACS"},
    {"pacs_aet": "synapse", "pacs_name": "Synapse"},
]
MODALITIES = ["CT", "MR", "PET", "CR", "US"]


fake = Faker()


def feed_report(body: str):
    report = ReportFactory.create(body=body)
    groups = fake.random_elements(elements=list(Group.objects.all()), unique=True)
    report.groups.set(groups)
    for handler in report_event_handlers:
        handler("created", report)


def feed_reports():
    samples_path = Path(settings.BASE_DIR / "samples" / "reports.json")
    with open(samples_path, "r") as f:
        reports = json.load(f)

    for report in reports:
        feed_report(report)


def create_users() -> list[User]:
    if "ADMIN_USERNAME" not in environ or "ADMIN_PASSWORD" not in environ:
        print("Cave! No admin credentials found in environment. Using default ones.")

    admin_data = {
        "username": environ.get("ADMIN_USERNAME", "admin"),
        "first_name": environ.get("ADMIN_FIRST_NAME", "Wilhelm"),
        "last_name": environ.get("ADMIN_LAST_NAME", "Röntgen"),
        "email": environ.get("ADMIN_EMAIL", "wilhelm.roentgen@example.org"),
        "password": environ.get("ADMIN_PASSWORD", "mysecret"),
    }
    admin = AdminUserFactory.create(**admin_data)

    TokenFactory.create(
        token_hashed=hash_token(ADMIN_AUTH_TOKEN),
        fraction=ADMIN_AUTH_TOKEN[:FRACTION_LENGTH],
        owner=admin,
        expires=None,
    )

    users = [admin]

    urgent_permissions = Permission.objects.filter(
        codename="can_process_urgently",
    )
    unpseudonymized_permissions = Permission.objects.filter(
        codename="can_transfer_unpseudonymized",
    )

    user_count = USER_COUNT - 1  # -1 for admin
    for i in range(user_count):
        user = UserFactory.create()

        if i > 0:
            user.user_permissions.add(*urgent_permissions)
            user.user_permissions.add(*unpseudonymized_permissions)

        users.append(user)

    return users


def create_groups(users: list[User]) -> list[Group]:
    groups: list[Group] = []

    for _ in range(GROUP_COUNT):
        group = GroupFactory.create()
        groups.append(group)

    for user in users:
        group: Group = fake.random_element(elements=groups)
        user.groups.add(group)
        if not user.active_group:
            user.change_active_group(group)

    return groups


class Command(BaseCommand):
    help = "Populates the database with example data."

    def handle(self, *args, **options):
        if User.objects.count() > 0:
            print("Development database already populated. Skipping.")
        else:
            print("Populating development database with test data.")
            users = create_users()
            create_groups(users)

        if Report.objects.first():
            print("Reports already populated. Skipping.")
        else:
            print("Populating database with example reports.")
            feed_reports()
