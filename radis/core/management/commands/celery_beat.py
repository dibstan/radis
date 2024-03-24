from django.conf import settings

from adit_radis_shared.common.management.base.celery_beat import CeleryBeatCommand


class Command(CeleryBeatCommand):
    project = "radis"
    paths_to_watch = [settings.BASE_DIR / "radis"]
