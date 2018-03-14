import copy
from concurrent.futures import ThreadPoolExecutor

from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from health_check.plugins import plugin_dir


class MainView(TemplateView):
    template_name = 'health_check/index.html'

    @never_cache
    def get(self, request, *args, **kwargs):
        errors = []

        plugins = sorted((
            plugin_class(**copy.deepcopy(options))
            for plugin_class, options in plugin_dir._registry
        ), key=lambda plugin: plugin.identifier())

        def _run(plugin):
            plugin.run_check()
            try:
                return plugin.errors
            finally:
                from django.db import connection
                connection.close()

        with ThreadPoolExecutor(max_workers=len(plugins) or 1) as executor:
            for ers in executor.map(_run, plugins):
                errors.extend(ers)

        status_code = 500 if errors else 200
        return HttpResponse(
            'pong' if status_code == 200 else 'sweaty',
            status=status_code
        )
