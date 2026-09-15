# QUICK START GUIDE

## 🚀 Get Started Manually

### Prerequisites

- Python 3.11 or newer
- Oracle Database 19c or newer
- Oracle SQL Developer

### 1. Set Up the Database

In Oracle SQL Developer, connect to your Oracle schema and run
`database/schema.sql`, followed by `database/sample_data.sql`.

### 2. Start the Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` with your Oracle credentials, then run:

```bash
python run.py
```

The API is available at http://localhost:8000.

### 3. Start the Frontend

Open a second terminal:

```bash
cd frontend
python -m http.server 3000
```

The dashboard is available at http://localhost:3000.

### Verify Everything is Running

```bash
# Check backend health
curl http://localhost:8000/health

# Check if you can fetch shipments
curl http://localhost:8000/api/shipments/

# Backend logs appear in the terminal running `python run.py`.
```

---

## 🔧 Manual Development Setup Details

### Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env

# Edit .env with your Oracle credentials
# Defaults:
# DATABASE_HOST=localhost
# DATABASE_PORT=1521
# DATABASE_USER=supply_chain
# DATABASE_PASSWORD=your_password
# DATABASE_SERVICE_NAME=XEPDB1

# Run backend
python run.py
# Should see: Uvicorn running on http://0.0.0.0:8000
```

### Database Setup (Oracle SQL Developer)

```bash
# Connect to Oracle in SQL Developer.
# Run database/schema.sql first, then database/sample_data.sql.
```

### Frontend Setup

```bash
cd frontend

# Option A: Simple HTTP Server (Python)
python -m http.server 3000
# Open browser: http://localhost:3000

# Option B: Open index.html directly in browser
# File -> Open File -> select index.html

# Option C: Use Node.js http-server (if installed)
npx http-server -p 3000
```

---

## 📋 Verify Installation

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Get all shipments
curl http://localhost:8000/api/shipments/

# Get dashboard summary
curl http://localhost:8000/api/shipments/summary/dashboard
```

### Test Frontend

1. Open http://localhost:3000 in browser
2. Check "Dashboard" tab loads
3. Verify KPI cards show numbers (not "Loading...")
4. Check "API Connected" status in header

### Test Database

```bash
# From MySQL CLI:
USE supply_chain_db;
SELECT COUNT(*) as shipment_count FROM shipments;
SELECT * FROM disruptions WHERE is_active = 1;
```

---

## 🎯 Understanding the Sample Data

### Pre-loaded Shipments

- **SHIP-001**: Chicago → Miami (Cold Chain - Vaccines, $500K)
- **SHIP-002**: Newark → LA (Cold Chain - Fruits, $75K)
- **SHIP-003**: Houston → NYC (Electronics, $250K)
- **SHIP-004**: San Francisco → Seattle (Electronics, $150K)
- **SHIP-005**: Miami → Orlando (Cold Chain - Seafood, $120K)

### Active Disruptions

- **DISR-001**: Port of Miami Strike (Affects SHIP-001, SHIP-005)
- **DISR-002**: Winter Storm Northeast (Affects routes to NYC)
- **DISR-003**: LA Port Congestion (Affects SHIP-002)

### Fleet Assets

- 3 Trucks (1 idle, 2 in transit)
- 2 Containers (1 idle, 1 in transit)
- 2 Vessels (1 in transit, 1 idle)

### Cold Chain Alerts

- 2 Temperature Excursion Alerts (1 Warning, 1 Critical)
- FDA Regulatory Impact Classification

---

## 🔍 First Steps to Explore

### 1. View Dashboard

- Click "Dashboard" tab
- See all KPIs loading
- Review "Critical Temperature Alerts"
- Review "Active Disruptions"

### 2. View Affected Shipments

- Click "Disruptions" tab
- Click on "Port of Miami Strike"
- Notice 2 cold chain shipments affected
- Review "Winter Storm" (3 shipments affected)

### 3. Check Fleet Status

- Click "Fleet" tab
- Filter by "Idle" to see available assets
- Check "Cold Chain Capable" filter
- Note which assets can be deployed

### 4. Monitor Cold Chain

- Click "Cold Chain" tab
- See temperature readings
- Review critical alert for SHIP-001
- Notice FDA regulatory impact message

### 5. Try API Directly

- Open http://localhost:8000/docs
- Explore interactive API documentation
- Try "GET /shipments" endpoint
- Try "GET /disruptions"

---

## 🐛 Troubleshooting

### "Cannot connect to API" Error

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start backend:
cd backend && python run.py

# Check the terminal running the backend for errors.
```

### "Database connection failed" Error

```bash
# Check the Oracle listener and database service are running
# Verify .env credentials and DATABASE_SERVICE_NAME match SQL Developer
# Check DATABASE_HOST and DATABASE_PORT are correct

# Test the same host, port, service name, and credentials in SQL Developer
```

### Frontend shows "Loading..." Forever

```bash
# Check browser console (F12) for errors
# Verify API_BASE_URL in app.js points to correct backend
# Check CORS is not blocking requests:
curl -i http://localhost:8000/api/shipments/
# Should see: Access-Control-Allow-Origin: *
```

### "Port already in use" Error

```bash
# If port 8000 is busy:
# Change API_PORT in backend/.env

# If port 3000 is busy:
# Use different port: python -m http.server 3001
```

---

## 📊 Dashboard Walkthrough

### KPI Cards

- **Total Shipments**: 5 loaded
- **In Transit**: 3
- **Delayed**: 1
- **Delivered**: 1
- **Cold Chain Shipments**: 2
- **High Risk Shipments**: 1 (has temperature alert)
- **Active Disruptions**: 3
- **Affected Shipments**: 2 (from disruptions)
- **Critical Disruptions**: 1
- **Total Fleet Assets**: 7
- **Idle Assets**: 3 (available for deployment)

### Critical Alerts Panel

Shows 2 temperature excursions:

1. **SHIP-001**: Temperature 8.5°C (exceeds 8°C max)
   - Severity: WARNING
   - FDA Compliance: Potential issue, requires QA review

2. **SHIP-005**: Temperature 1.2°C (below 2°C min)
   - Severity: CRITICAL
   - FDA Compliance: Likely violation, possible destruction

### Active Disruptions Panel

Shows 3 events:

1. **Port of Miami Strike** - 2 affected shipments
2. **Winter Storm Northeast** - 3 affected shipments
3. **LA Port Congestion** - 1 affected shipment

---

## 🚀 Next Steps

### Try These Actions

1. **Update a Shipment Status**
   - Go to Shipments tab
   - Click "View" on SHIP-003
   - Change status to "in_transit"

2. **Deploy an Idle Asset**
   - Go to Fleet tab
   - Filter for "Idle" status
   - Click "Deploy" on TRUCK-001
   - Assign to SHIP-003
   - Observe status changes to "in_transit"

3. **Create a New Disruption**
   - Go to Disruptions tab
   - Try creating a new disruption via API:

   ```bash
   curl -X POST http://localhost:8000/api/disruptions/ \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Typhoon Alert",
       "description": "Tropical storm approaching Pacific routes",
       "disruption_type": "weather",
       "affected_region": "Los Angeles, CA",
       "severity": "high",
       "start_time": "2024-01-10T14:00:00",
       "estimated_resolution": "2024-01-12T18:00:00"
     }'
   ```

4. **Log a Temperature Reading**
   - Go to Cold Chain tab
   - Log sensor data via API:
   ```bash
   curl -X POST http://localhost:8000/api/cold-chain/sensors \
     -H "Content-Type: application/json" \
     -d '{
       "sensor_id": "SENSOR-NEW",
       "shipment_id": "SHIP-001",
       "container_id": "CONT-001",
       "temperature": 3.5,
       "humidity": 50,
       "timestamp": "2024-01-10T14:30:00"
     }'
   ```

---

## 📚 Documentation Links

- **Full README**: See [README.md](README.md)
- **API Examples**: See [API_EXAMPLES.md](API_EXAMPLES.md)
- **API Swagger**: http://localhost:8000/docs (when backend running)
- **Database Schema**: See [database/schema.sql](database/schema.sql)

---

## ✅ Success Indicators

If you see these, everything is working:

✓ Dashboard loads with KPI cards showing numbers
✓ "API Connected" shows in header
✓ Temperature alerts display with regulatory impact
✓ Active disruptions list shows 3 disruptions
✓ Fleet assets table shows 7 assets
✓ Shipments table shows 5 shipments
✓ API responses work (curl commands succeed)
✓ Browser console (F12) shows no errors

---

## 🆘 Need Help?

### Python/Virtual Environment Issues

```bash
# Recreate venv
rmdir venv  # or rm -rf venv on Mac/Linux
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Database Issues

```bash
# Drop and recreate the Oracle user's tables in SQL Developer if needed.
# Re-run schema.sql and sample_data.sql.
```

---

**You're all set! 🎉**

Start exploring the dashboard and API. Happy supply chain optimizing!
