from django.urls import path
from . import views

app_name = "omada"

urlpatterns = [
    path("api/devices/update/", views.device_update, name="device_update"),
    path("api/clients/update/", views.client_update, name="client_update"),
    path("api/devices/", views.device_list, name="device_list"),
    path("api/clients/", views.client_list, name="client_list"),
    path("api/portal/login/", views.portal_login, name="portal_login"),
    path("api/portal/auth/", views.portal_auth, name="portal_auth"),
    path("api/portal/status/", views.portal_status, name="portal_status"),
    path("api/portal/logout/", views.portal_logout, name="portal_logout"),
]
