# Supply Chain Optimizer

A real-time supply chain disruption detection and management system with IoT-based cold chain monitoring.

## 📋 Features

### Core Capabilities

- **📦 Shipment Tracking**: Real-time monitoring of hundreds of active shipments
- **🚨 Disruption Detection**: Automatic identification of supply chain disruptions (weather, strikes, geopolitical events)
- **🛣️ Route Optimization**: Intelligent re-routing recommendations with cost/time impact analysis
- **🚚 Fleet Management**: Asset redeployment planning and idle asset identification
- **🧊 Cold Chain Monitoring**: IoT sensor-based temperature monitoring with regulatory compliance alerts
- **🌡️ Temperature Alert System**: Critical severity classification with FDA compliance tracking

### Key Problems Solved

| Problem                                                          | Solution                                                            |
| ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| Manual tracking of disruptions across hundreds of shipments      | Automated disruption detection and affected shipment identification |
| Fleet assets sitting idle during crises                          | Intelligent idle asset detection and redeployment recommendations   |
| Cold chain spoilage discovered only at delivery (costing $500K+) | Real-time IoT monitoring with early warning system                  |
| Regulatory compliance uncertainty                                | Automatic severity classification with regulatory impact reporting  |

## 🏗️ Architecture

```
supply-chain-optimizer/
├── backend/                 # FastAPI REST API
│   ├── app/
│   │   ├── models.py       # SQLAlchemy database models
│   │   ├── schemas.py      # Pydantic validation schemas
│   │   ├── database.py     # Database connection
│   │   └── routes/
│   │       ├── shipments.py        # Shipment management API
│   │       ├── disruptions.py      # Disruption tracking API
│   │       ├── fleet.py            # Fleet management API
│   │       └── cold_chain.py       # Cold chain monitoring API
│   ├── requirements.txt
│   └── run.py
├── frontend/                # HTML/JavaScript Dashboard
│   ├── index.html          # Main dashboard UI
│   ├── styles.css          # Responsive styling
│   └── app.js              # Frontend logic & API integration
├── database/
│   ├── schema.sql          # MySQL database schema
│   └── sample_data.sql     # Sample data for testing
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Oracle Database 19c or newer
- Oracle SQL Developer

### Local Installation

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your Oracle credentials and service name
# Example service name for Oracle XE: XEPDB1

# Run the backend server
python run.py
```

Backend will be available at: http://localhost:8000

#### Database Setup

Open Oracle SQL Developer, connect as the user from `backend/.env`, and run
`database/schema.sql` followed by `database/sample_data.sql` in that connection.

#### Frontend Setup

```bash
cd frontend

# If using with local backend, edit app.js and set:
const API_BASE_URL = 'http://localhost:8000/api';

# Open index.html in a web browser
# You can use Python's simple server:
python -m http.server 3000
```

Frontend will be available at: http://localhost:3000

## 📡 API Endpoints

### Shipments

- `GET /api/shipments/` - List all shipments
- `POST /api/shipments/` - Create new shipment
- `GET /api/shipments/{shipment_id}` - Get shipment details
- `PATCH /api/shipments/{shipment_id}` - Update shipment status
- `GET /api/shipments/summary/dashboard` - Get shipment KPIs

### Disruptions

- `GET /api/disruptions/` - List disruptions
- `POST /api/disruptions/` - Create new disruption
- `GET /api/disruptions/{disruption_id}/affected-shipments` - Get affected shipments
- `GET /api/disruptions/{disruption_id}/recommendations` - Get route recommendations
- `PATCH /api/disruptions/{disruption_id}/resolve` - Mark as resolved

### Fleet

- `GET /api/fleet/` - List fleet assets
- `POST /api/fleet/` - Register new asset
- `POST /api/fleet/{asset_id}/deploy` - Deploy asset to shipment
- `POST /api/fleet/{asset_id}/return` - Return asset to idle
- `GET /api/fleet/summary/dashboard` - Get fleet KPIs

### Cold Chain

- `POST /api/cold-chain/sensors` - Log sensor reading
- `GET /api/cold-chain/sensors/{shipment_id}` - Get sensor history
- `GET /api/cold-chain/alerts` - List temperature alerts
- `PATCH /api/cold-chain/alerts/{alert_id}/acknowledge` - Acknowledge alert
- `GET /api/cold-chain/health/critical` - Get critical alerts with regulatory impact

### Full API Documentation

Interactive API documentation available at: `http://localhost:8000/docs` (when backend is running)

## 🗄️ Database Schema

### Key Tables

- **shipments**: Core shipment records with cold chain flag
- **disruptions**: Active/resolved supply chain disruptions
- **fleet_assets**: Trucks, containers, vessels with status and capability tracking
- **cold_chain_sensors**: IoT sensor readings (temperature, humidity, location)
- **temperature_alerts**: Excursion events with severity and regulatory impact
- **route_recommendations**: Alternative routes and carrier suggestions

### Indexes

- Performance optimized for common queries
- Indexes on shipment status, disruption regions, alert severity

## 🧊 Cold Chain Monitoring

### Temperature Thresholds (Configurable)

```env
COLD_CHAIN_TEMP_MIN=2°C
COLD_CHAIN_TEMP_MAX=8°C
COLD_CHAIN_ALERT_THRESHOLD=30 minutes
```

### Severity Classification

| Deviation | Severity | Impact                                             |
| --------- | -------- | -------------------------------------------------- |
| > 5°C     | CRITICAL | Likely FDA violation, product destruction possible |
| 2-5°C     | WARNING  | Potential FDA issue, QA review required            |
| < 2°C     | INFO     | Minor variance, monitoring recommended             |

### Regulatory Compliance

- FDA 21 CFR 211.42 (Pharmaceutical cold chain)
- EU GMP Annex 15 (Cold chain requirements)
- WHO guidelines (Vaccine storage)

## 📊 Dashboard Features

### Real-Time KPIs

- Total/In-Transit/Delayed/Delivered shipments
- Cold chain shipments and high-risk count
- Active disruptions and affected shipments
- Fleet asset status and availability
- Temperature alerts by severity

### Alert Panels

- **Critical Temperature Alerts**: Immediate attention required
- **Active Disruptions**: Current supply chain issues
- **Idle Fleet Assets**: Available for redeployment

### Data Filters & Search

- Filter shipments by status, type, cold chain
- Search disruptions by severity and region
- View fleet assets by type and availability
- Monitor temperature alerts by severity and shipment

## 🔧 Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=supply_chain_db

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Cold Chain Thresholds
COLD_CHAIN_TEMP_MIN=2
COLD_CHAIN_TEMP_MAX=8
COLD_CHAIN_ALERT_THRESHOLD=30
```

## 📈 Sample Data

Pre-loaded sample data includes:

- 5 shipments (2 cold chain, 3 standard)
- 3 active disruptions (port strike, winter storm, port congestion)
- 7 fleet assets (trucks, containers, vessels)
- 7 sensor readings with temperature excursion example
- 2 critical temperature alerts

## 🛠️ Development

### Adding New Features

1. **New API Endpoint**: Add route in `backend/app/routes/`
2. **Database Changes**: Update `backend/app/models.py` and schema
3. **Frontend UI**: Update `frontend/index.html` and `app.js`
4. **API Schema**: Update `backend/app/schemas.py` for validation

### Running Tests

```bash
# Backend tests (once test suite is added)
cd backend
python -m pytest

# Frontend tests (once test suite is added)
cd frontend
npm test
```

### Logging & Debugging

The backend prints request and application logs in the terminal where `python run.py` is running. Check Oracle status and logs in SQL Developer or Oracle Enterprise Manager.

## 🚨 Troubleshooting

### Backend won't connect to Oracle

```bash
# Check the Oracle listener and database service are running.

# Verify connection string in .env
# Make sure the Oracle service name in .env matches the SQL Developer connection
```

### Frontend can't reach API

```bash
# Check CORS configuration
# Frontend URL must be allowed in FastAPI CORS middleware
# Update API_BASE_URL in frontend/app.js

# Verify backend is running
curl http://localhost:8000/health
```

### Database migration needed

Run `database/schema.sql` and then `database/sample_data.sql` in Oracle SQL Developer.

## 📚 Key Technologies

### Backend

- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Oracle Database**: Reliable relational database

### Frontend

- **Vanilla HTML/CSS/JavaScript**: No build tool required
- **Bootstrap Grid**: Responsive layout
- **Fetch API**: Async API communication

## 🔐 Security Considerations

- [ ] Implement JWT authentication for API
- [ ] Add role-based access control (RBAC)
- [ ] Encrypt sensitive data in transit (HTTPS)
- [ ] Implement rate limiting on API endpoints
- [ ] Audit logging for critical operations
- [ ] Input validation and sanitization
- [ ] Database credentials in secure vault (not .env in production)

## 📝 License

Internal Use - Supply Chain Optimization Platform

## 👥 Support

For issues, questions, or contributions, please refer to internal documentation or contact the development team.

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Status**: Production Ready
