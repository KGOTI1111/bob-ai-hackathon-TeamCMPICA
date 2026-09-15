# API Usage Examples

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently no authentication required. In production, implement JWT token-based auth.

---

## 1. Shipments API

### List All Shipments

```bash
curl http://localhost:8000/api/shipments/
```

**Query Parameters:**

- `status`: pending, in_transit, delayed, diverted, delivered, cancelled
- `is_cold_chain`: true/false
- `skip`: Pagination offset (default: 0)
- `limit`: Page size (default: 100)

**Example with filters:**

```bash
curl "http://localhost:8000/api/shipments/?status=in_transit&is_cold_chain=true&limit=50"
```

### Get Shipment Details

```bash
curl http://localhost:8000/api/shipments/SHIP-001
```

### Create New Shipment

```bash
curl -X POST http://localhost:8000/api/shipments/ \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHIP-006",
    "origin": "Los Angeles, CA",
    "destination": "New York, NY",
    "cargo_description": "Electronics",
    "cargo_value": 250000.00,
    "is_cold_chain": false,
    "carrier": "FastFreight",
    "container_id": "CONT-006",
    "planned_delivery": "2024-01-22T18:00:00"
  }'
```

### Update Shipment Status

```bash
curl -X PATCH http://localhost:8000/api/shipments/SHIP-001 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_transit",
    "current_location": "Memphis, TN",
    "estimated_delivery": "2024-01-14T10:00:00"
  }'
```

### Get Shipment Dashboard Summary

```bash
curl http://localhost:8000/api/shipments/summary/dashboard
```

**Response:**

```json
{
  "total_shipments": 5,
  "in_transit": 3,
  "delayed": 1,
  "delivered": 1,
  "cold_chain_shipments": 2,
  "high_risk_shipments": 1
}
```

---

## 2. Disruptions API

### List Active Disruptions

```bash
curl "http://localhost:8000/api/disruptions/?is_active=true&severity=high"
```

### Create New Disruption

```bash
curl -X POST http://localhost:8000/api/disruptions/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Port of Oakland Closure",
    "description": "Emergency closure due to security breach",
    "disruption_type": "geopolitical",
    "affected_region": "Oakland, CA",
    "severity": "critical",
    "start_time": "2024-01-10T14:00:00",
    "estimated_resolution": "2024-01-12T18:00:00"
  }'
```

### Get Affected Shipments

```bash
curl http://localhost:8000/api/disruptions/DISR-001/affected-shipments
```

### Get Route Recommendations

```bash
curl http://localhost:8000/api/disruptions/DISR-001/recommendations
```

### Create Route Recommendation

```bash
curl -X POST http://localhost:8000/api/disruptions/DISR-001/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHIP-001",
    "disruption_id": "DISR-001",
    "original_route": "Chicago -> Miami (Port)",
    "recommended_route": "Chicago -> Jacksonville (Port)",
    "alternative_carrier": "ColdChain Express",
    "cost_impact": 5000.00,
    "time_impact_hours": 6,
    "risk_score": 25.0
  }'
```

### Mark Disruption as Resolved

```bash
curl -X PATCH http://localhost:8000/api/disruptions/DISR-001/resolve
```

### Get Disruption Summary

```bash
curl http://localhost:8000/api/disruptions/summary/dashboard
```

---

## 3. Fleet Management API

### List Fleet Assets

```bash
curl "http://localhost:8000/api/fleet/?asset_type=truck&status=idle"
```

**Query Parameters:**

- `status`: idle, in_transit, maintenance
- `asset_type`: truck, container, vessel
- `is_available`: true/false

### Register New Fleet Asset

```bash
curl -X POST http://localhost:8000/api/fleet/ \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "TRUCK-004",
    "asset_type": "truck",
    "status": "idle",
    "current_location": "Phoenix, AZ",
    "capacity_tons": 20.0,
    "is_cold_chain_capable": true
  }'
```

### Deploy Asset to Shipment

```bash
curl -X POST http://localhost:8000/api/fleet/TRUCK-001/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHIP-003",
    "location": "Houston, TX"
  }'
```

### Return Asset to Idle

```bash
curl -X POST http://localhost:8000/api/fleet/TRUCK-001/return
```

### Get Available Assets for Redeployment

```bash
curl "http://localhost:8000/api/fleet/available/candidates?asset_type=truck&is_cold_chain=true&min_capacity=18"
```

### Get Fleet Summary

```bash
curl http://localhost:8000/api/fleet/summary/dashboard
```

---

## 4. Cold Chain Monitoring API

### Log Sensor Reading

```bash
curl -X POST http://localhost:8000/api/cold-chain/sensors \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "SENSOR-003",
    "shipment_id": "SHIP-002",
    "container_id": "CONT-002",
    "temperature": 7.5,
    "humidity": 55.0,
    "latitude": 35.0829,
    "longitude": -106.6504,
    "timestamp": "2024-01-10T12:30:00"
  }'
```

### Get Sensor Readings for Shipment

```bash
curl "http://localhost:8000/api/cold-chain/sensors/SHIP-001?hours=24&limit=100"
```

### List Temperature Alerts

```bash
curl "http://localhost:8000/api/cold-chain/alerts?severity=critical&acknowledged=false"
```

**Query Parameters:**

- `severity`: info, warning, critical
- `acknowledged`: true/false

### Get Alert Details

```bash
curl http://localhost:8000/api/cold-chain/alerts/ALERT-001
```

### Acknowledge Temperature Alert

```bash
curl -X PATCH http://localhost:8000/api/cold-chain/alerts/ALERT-001/acknowledge
```

### Get Critical Cold Chain Shipments

```bash
curl http://localhost:8000/api/cold-chain/health/critical
```

**Response Example:**

```json
[
  {
    "alert_id": "ALERT-001",
    "shipment_id": "SHIP-001",
    "temperature": 8.5,
    "expected_range": "2°C - 8°C",
    "severity": "warning",
    "regulatory_impact": "WARNING: Potential FDA compliance issue...",
    "timestamp": "2024-01-10T10:00:00",
    "cargo_value": 500000.0,
    "origin": "Chicago, IL",
    "destination": "Miami, FL"
  }
]
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200 OK**: Successful GET/PATCH
- **201 Created**: Successful POST
- **400 Bad Request**: Invalid input
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

**Error Response Format:**

```json
{
  "detail": "Shipment not found"
}
```

---

## Rate Limiting & Performance

- No rate limiting currently implemented
- Paginate large result sets with `skip` and `limit`
- Recommended: `limit=50` for large tables
- Use filters to reduce result sets

---

## Testing with cURL

### Create a test shipment and track it

```bash
#!/bin/bash

# 1. Create shipment
curl -X POST http://localhost:8000/api/shipments/ \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "TEST-001",
    "origin": "Test Origin",
    "destination": "Test Destination",
    "cargo_description": "Test Cargo",
    "cargo_value": 10000,
    "is_cold_chain": true,
    "carrier": "Test Carrier",
    "container_id": "TEST-001",
    "planned_delivery": "2024-01-20T00:00:00"
  }'

# 2. Get shipment
curl http://localhost:8000/api/shipments/TEST-001

# 3. Log sensor readings
curl -X POST http://localhost:8000/api/cold-chain/sensors \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "TEST-SENSOR-001",
    "shipment_id": "TEST-001",
    "container_id": "TEST-001",
    "temperature": 10.5,
    "humidity": 60,
    "timestamp": "2024-01-10T12:00:00"
  }'

# 4. Check for alerts
curl http://localhost:8000/api/cold-chain/alerts?shipment_id=TEST-001
```

---

## Integration Example (Python)

```python
import requests
import json

API_BASE = "http://localhost:8000/api"

# Create shipment
shipment = {
    "shipment_id": "PY-001",
    "origin": "Seattle, WA",
    "destination": "Portland, OR",
    "cargo_description": "Tech equipment",
    "cargo_value": 150000,
    "is_cold_chain": False,
    "carrier": "FastFreight",
    "container_id": "PY-001",
    "planned_delivery": "2024-01-15T18:00:00"
}

response = requests.post(f"{API_BASE}/shipments/", json=shipment)
print("Created:", response.json())

# Update status
update = {
    "status": "in_transit",
    "current_location": "Portland, OR"
}

response = requests.patch(f"{API_BASE}/shipments/PY-001", json=update)
print("Updated:", response.json())

# Get dashboard summary
response = requests.get(f"{API_BASE}/shipments/summary/dashboard")
print("Summary:", response.json())
```

---

For more information, visit http://localhost:8000/docs when backend is running.
