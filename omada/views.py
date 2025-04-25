from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
import json
import requests
from datetime import timedelta
from .models import OmadaDevice, OmadaClient, PortalSession

# Create your views here.

import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def device_update(request):
    """
    Handle device updates from Omada Cloud Controller.
    Expected JSON payload:
    {
        "device_id": "string",
        "name": "string",
        "mac_address": "string",
        "ip_address": "string",
        "model": "string",
        "firmware_version": "string",
        "status": "string"
    }
    """
    try:
        data = json.loads(request.body)
        device, created = OmadaDevice.objects.update_or_create(
            device_id=data["device_id"],
            defaults={
                "name": data["name"],
                "mac_address": data["mac_address"],
                "ip_address": data.get("ip_address"),
                "model": data["model"],
                "firmware_version": data["firmware_version"],
                "status": data["status"],
                "last_seen": timezone.now(),
            },
        )
        return JsonResponse(
            {
                "status": "success",
                "message": "Device updated successfully",
                "created": created,
            }
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def client_update(request):
    """
    Handle client updates from Omada Cloud Controller.
    Expected JSON payload:
    {
        "client_id": "string",
        "mac_address": "string",
        "ip_address": "string",
        "hostname": "string",
        "device_id": "string"
    }
    """
    try:
        data = json.loads(request.body)
        device = OmadaDevice.objects.get(device_id=data["device_id"])
        client, created = OmadaClient.objects.update_or_create(
            client_id=data["client_id"],
            defaults={
                "mac_address": data["mac_address"],
                "ip_address": data.get("ip_address"),
                "hostname": data.get("hostname"),
                "device": device,
                "last_seen": timezone.now(),
            },
        )
        return JsonResponse(
            {
                "status": "success",
                "message": "Client updated successfully",
                "created": created,
            }
        )
    except OmadaDevice.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Device not found"}, status=404
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@require_http_methods(["GET"])
def device_list(request):
    """
    Return a list of all devices.
    """
    devices = OmadaDevice.objects.all()
    return JsonResponse({"status": "success", "devices": list(devices.values())})


@require_http_methods(["GET"])
def client_list(request):
    """
    Return a list of all clients.
    """
    clients = OmadaClient.objects.all()
    return JsonResponse({"status": "success", "clients": list(clients.values())})


@require_http_methods(["GET", "POST", "OPTIONS"])
@csrf_exempt
def portal_login(request: HttpRequest):
    """
    Handle portal login page request.
    Expected query parameters:
    - clientMac: Client MAC address
    - apMac: AP MAC address (for wireless)
    - gatewayMac: Gateway MAC address (for wired)
    - ssidName: SSID name (for wireless)
    - vid: VLAN ID (for wired)
    - radioId: Radio ID (for wireless)
    - site: Site name
    - redirectUrl: URL to redirect after authentication
    - t: Timestamp
    """
    if request.method == "POST":
        return portal_auth(request)
    try:
        # Create or update portal session
        session, updated = PortalSession.objects.update_or_create(
            client_mac=request.GET.get("clientMac"),
            defaults={
                "ap_mac": request.GET.get("apMac"),
                "gateway_mac": request.GET.get("gatewayMac"),
                "ssid_name": request.GET.get("ssidName"),
                "vlan_id": request.GET.get("vid"),
                "radio_id": request.GET.get("radioId"),
                "site_name": request.GET.get("site"),
                "redirect_url": request.GET.get("redirectUrl"),
                "expires_at": timezone.now() + timedelta(hours=24),
            },
        )

        # Render login page
        return render(
            request,
            "omada/portal_login.html",
            {
                "session": session,
                "client_mac": session.client_mac,
                "site_name": session.site_name,
                "redirect_url": session.redirect_url,
            },
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


def get_omada_token(username, password):
    """
    Get authentication token from Omada Controller.

    Args:
        username (str): Omada Controller username
        password (str): Omada Controller password

    Returns:
        str: Authentication token if successful, None otherwise
    """
    print("getting omada token")
    try:
        login_url = f"{settings.OMADA_CONTROLLER_URL}api/v2/hotspot/login"
        print("login_url:  ", login_url)
        response = requests.post(
            login_url,
            json={"name": username, "password": password},
            verify=settings.OMADA_CONTROLLER_VERIFY_SSL,
        )

        print("omada content:  ", response.text)
        print("omada headers:  ", response.headers)
        if response.status_code == 200:
            data = response.json()
            if (
                data.get("errorCode") == 0
                and "result" in data
                and "token" in data["result"]
            ):
                return data["result"]["token"]

        return None
    except Exception as e:
        print(f"Error getting Omada token: {str(e)}")
        return None


def portal_auth(request: HttpRequest):
    """
    Handle portal authentication request.
    Expected JSON payload:
    {
        "clientMac": "string",
        "apMac": "string",
        "gatewayMac": "string",
        "ssidName": "string",
        "vid": "string",
        "radioId": "string",
        "site": "string",
        "time": "string"
    }
    """
    try:
        data: dict = {
            **request.GET,
            **{
                "username": request.POST.get("username"),
                "password": request.POST.get("password"),
                "clientMac": request.POST.get("clientMac"),
                "siteName": request.POST.get("siteName"),
                "session": request.POST.get("session"),
            },
        }

        session = PortalSession.objects.get(
            client_mac=data["clientMac"],
        )

        # Get username and password from the request
        username = data.get("username")
        password = data.get("password")

        if not (username == "user" and password == "Somepassword1!"):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Invalid username or password you cannot browse this site.",
                },
                status=401,
            )
        # Get Omada token
        token = get_omada_token(
            settings.OMADA_CONTROLLER_USERNAME, settings.OMADA_CONTROLLER_PASSWORD
        )

        if not token:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Failed to authenticate with Omada Controller",
                },
                status=401,
            )

        # Update session with authentication token
        session.token = token
        session.is_authenticated = True
        session.save()

        # Send authentication to Omada Controller
        controller_url = f"{settings.OMADA_CONTROLLER_URL}api/v2/hotspot/extPortal/auth"
        auth_data = {
            "clientMac": data["clientMac"],
            "site": session.site_name,
            "time": 60 * 5 * 1000,  # 5 minutes in milliseconds
            "authType": 4,
        }

        if session.ap_mac:
            auth_data.update(
                {
                    "apMac": session.ap_mac,
                    "ssidName": session.ssid_name,
                    "radioId": session.radio_id,
                }
            )
        else:
            auth_data.update(
                {"gatewayMac": session.gateway_mac, "vid": session.vlan_id}
            )

        logger.info(f"auth_data:  {auth_data}")
        print(f"auth_data:  {auth_data}. url: {controller_url}")

        response = requests.post(
            controller_url,
            json=auth_data,
            headers={
                "Csrf-Token": token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            verify=settings.OMADA_CONTROLLER_VERIFY_SSL,
        )

        print("response:  ", response.text)
        print("response headers:  ", response.headers)
        if response.status_code == 200:
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Authentication successful continue browsing",
                }
            )
        else:
            return JsonResponse(
                {"status": "error", "message": "Controller authentication failed"},
                status=400,
            )

    except PortalSession.DoesNotExist:
        print("PortalSession.DoesNotExist")
        return JsonResponse(
            {"status": "error", "message": "Session not found"}, status=404
        )
    except Exception as e:
        logger.error(f"Error in portal_auth: {str(e)}", exc_info=True)
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@require_http_methods(["GET"])
def portal_status(request):
    """
    Check portal authentication status.
    Expected query parameters:
    - clientMac: Client MAC address
    """
    try:
        session = PortalSession.objects.get(client_mac=request.GET.get("clientMac"))
        return JsonResponse(
            {
                "status": "success",
                "is_authenticated": session.is_authenticated,
                "expires_at": session.expires_at.isoformat(),
            }
        )
    except PortalSession.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Session not found"}, status=404
        )


@require_http_methods(["POST"])
def portal_logout(request):
    """
    Handle portal logout request.
    Expected JSON payload:
    {
        "clientMac": "string"
    }
    """
    try:
        data = json.loads(request.body)
        session = PortalSession.objects.get(client_mac=data["clientMac"])
        session.is_authenticated = False
        session.save()
        return JsonResponse({"status": "success"})
    except PortalSession.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Session not found"}, status=404
        )
