"""
This reroutes from an URL to a python view-function/class.

The main web/urls.py includes these routes for all urls (the root of the url)
so it can reroute to all website pages.

"""

from django.urls import path

from evennia.web.website.urls import urlpatterns as evennia_website_urlpatterns

from web.website.views.healthcheck import health as health_view

# add patterns here
urlpatterns = [
    # /health — JSON status endpoint (nginx / uptime monitors).
    # Responde 200 si DB OK, 503 si DB caída. Ver views/healthcheck.py.
    path("health", health_view, name="health"),
    path("health/", health_view),
]

# read by Django
urlpatterns = urlpatterns + evennia_website_urlpatterns
