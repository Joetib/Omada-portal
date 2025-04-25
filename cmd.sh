curl -X POST http://localhost:8000/omada/api/devices/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device123",
    "name": "AP-1",
    "mac_address": "DC-62-79-60-10-AA",
    "ip_address": "154.161.33.67",
    "model": "EAP660",
    "firmware_version": "1.0.0",
    "status": "online"
  }'