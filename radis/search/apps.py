from django.apps import AppConfig
from django.db.models.signals import post_migrate


class SearchConfig(AppConfig):
    name = "radis.search"

    def ready(self):
        register_app()

        # Put calls to db stuff in this signal handler
        post_migrate.connect(init_db, sender=self)


def register_app():
    from radis.core.site import register_main_menu_item

    register_main_menu_item(
        url_name="search",
        label="Search",
    )


def init_db(**kwargs):
    create_app_settings()


def create_app_settings():
    from .models import SearchAppSettings

    settings = SearchAppSettings.get()
    if not settings:
        SearchAppSettings.objects.create()
