from django.db import models
from django.utils import timezone


class OmadaDevice(models.Model):
    """
    Model to store information about Omada devices.
    """

    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    mac_address = models.CharField(max_length=17)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    model = models.CharField(max_length=100)
    firmware_version = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    last_seen = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    class Meta:
        ordering = ["-last_seen"]


class OmadaClient(models.Model):
    """
    Model to store information about clients connected to Omada devices.
    """

    client_id = models.CharField(max_length=100, unique=True)
    mac_address = models.CharField(max_length=17)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    hostname = models.CharField(max_length=200, null=True, blank=True)
    device = models.ForeignKey(
        OmadaDevice, on_delete=models.CASCADE, related_name="clients"
    )
    connected_since = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname or self.mac_address} ({self.client_id})"

    class Meta:
        ordering = ["-last_seen"]


class PortalSession(models.Model):
    """
    Model to store portal authentication sessions.
    """

    client_mac = models.CharField(max_length=17)
    ap_mac = models.CharField(max_length=17, null=True, blank=True)
    gateway_mac = models.CharField(max_length=17, null=True, blank=True)
    ssid_name = models.CharField(max_length=100, null=True, blank=True)
    vlan_id = models.CharField(max_length=10, null=True, blank=True)
    radio_id = models.CharField(max_length=10, null=True, blank=True)
    site_name = models.CharField(max_length=100)
    redirect_url = models.URLField()
    token = models.CharField(max_length=100, null=True, blank=True)
    is_authenticated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Session for {self.client_mac}"

    class Meta:
        ordering = ["-created_at"]
