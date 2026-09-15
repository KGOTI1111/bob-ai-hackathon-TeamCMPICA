"""
API routes for cold chain monitoring and temperature alert management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import (
    ColdChainSensor, TemperatureAlert, Shipment,
    TemperatureAlertSeverity
)
from app.schemas import (
    ColdChainSensorCreate, ColdChainSensor as ColdChainSensorSchema,
    TemperatureAlertCreate, TemperatureAlert as TemperatureAlertSchema
)
from typing import List
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/api/cold-chain", tags=["cold_chain"])

# Thresholds from environment
COLD_CHAIN_TEMP_MIN = float(os.getenv("COLD_CHAIN_TEMP_MIN", "2"))
COLD_CHAIN_TEMP_MAX = float(os.getenv("COLD_CHAIN_TEMP_MAX", "8"))
COLD_CHAIN_ALERT_THRESHOLD = int(os.getenv("COLD_CHAIN_ALERT_THRESHOLD", "30"))


@router.post("/sensors", response_model=ColdChainSensorSchema)
def log_sensor_reading(
    sensor_data: ColdChainSensorCreate,
    db: Session = Depends(get_db)
):
    """Log a temperature/humidity reading from IoT sensor"""
    db_sensor = ColdChainSensor(**sensor_data.dict())
    
    # Check for temperature excursion
    if (sensor_data.temperature < COLD_CHAIN_TEMP_MIN or
        sensor_data.temperature > COLD_CHAIN_TEMP_MAX):
        
        # Check if there's already an alert for this shipment
        existing_alert = db.query(TemperatureAlert).filter(
            TemperatureAlert.shipment_id == sensor_data.shipment_id,
            TemperatureAlert.timestamp >= datetime.utcnow() - timedelta(
                minutes=COLD_CHAIN_ALERT_THRESHOLD
            )
        ).first()
        
        if not existing_alert:
            # Create new temperature alert with severity classification
            severity = classify_severity(
                sensor_data.temperature,
                COLD_CHAIN_TEMP_MIN,
                COLD_CHAIN_TEMP_MAX
            )
            
            alert = TemperatureAlert(
                shipment_id=sensor_data.shipment_id,
                sensor_id=sensor_data.sensor_id,
                temperature_recorded=sensor_data.temperature,
                expected_min=COLD_CHAIN_TEMP_MIN,
                expected_max=COLD_CHAIN_TEMP_MAX,
                duration_minutes=1,
                severity=severity,
                timestamp=sensor_data.timestamp,
                regulatory_impact=get_regulatory_impact(severity)
            )
            db.add(alert)
    
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


@router.get("/sensors/{shipment_id}", response_model=List[ColdChainSensorSchema])
def get_shipment_sensor_readings(
    shipment_id: str,
    db: Session = Depends(get_db),
    hours: int = Query(24),
    skip: int = Query(0),
    limit: int = Query(1000)
):
    """Get recent sensor readings for a cold chain shipment"""
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment or not shipment.is_cold_chain:
        raise HTTPException(status_code=404, detail="Cold chain shipment not found")
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    readings = db.query(ColdChainSensor).filter(
        ColdChainSensor.shipment_id == shipment_id,
        ColdChainSensor.timestamp >= cutoff_time
    ).order_by(desc(ColdChainSensor.timestamp)).offset(skip).limit(limit).all()
    
    return readings


@router.get("/alerts", response_model=List[TemperatureAlertSchema])
def list_temperature_alerts(
    db: Session = Depends(get_db),
    severity: str = Query(None),
    acknowledged: bool = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """List temperature excursion alerts"""
    query = db.query(TemperatureAlert)
    
    if severity:
        query = query.filter(TemperatureAlert.severity == severity)
    if acknowledged is not None:
        query = query.filter(TemperatureAlert.acknowledged == acknowledged)
    
    return query.order_by(desc(TemperatureAlert.timestamp)).offset(skip).limit(limit).all()


@router.get("/alerts/{alert_id}", response_model=TemperatureAlertSchema)
def get_temperature_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a temperature alert"""
    alert = db.query(TemperatureAlert).filter(
        TemperatureAlert.alert_id == alert_id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """Mark an alert as acknowledged"""
    alert = db.query(TemperatureAlert).filter(
        TemperatureAlert.alert_id == alert_id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/health/critical", response_model=List[dict])
def get_critical_cold_chain_shipments(db: Session = Depends(get_db)):
    """Get shipments with critical temperature alerts"""
    critical_alerts = db.query(TemperatureAlert).filter(
        TemperatureAlert.severity == TemperatureAlertSeverity.critical,
        TemperatureAlert.acknowledged == False
    ).all()
    
    result = []
    for alert in critical_alerts:
        shipment = db.query(Shipment).filter(
            Shipment.shipment_id == alert.shipment_id
        ).first()
        
        result.append({
            "alert_id": alert.alert_id,
            "shipment_id": alert.shipment_id,
            "temperature": alert.temperature_recorded,
            "expected_range": f"{alert.expected_min}°C - {alert.expected_max}°C",
            "severity": alert.severity,
            "regulatory_impact": alert.regulatory_impact,
            "timestamp": alert.timestamp,
            "cargo_value": shipment.cargo_value if shipment else None,
            "origin": shipment.origin if shipment else None,
            "destination": shipment.destination if shipment else None
        })
    
    return result


def classify_severity(temperature: float, min_temp: float, max_temp: float) -> str:
    """Classify alert severity based on temperature deviation"""
    if temperature < min_temp:
        deviation = min_temp - temperature
    else:
        deviation = temperature - max_temp
    
    if deviation > 5:
        return TemperatureAlertSeverity.critical
    elif deviation > 2:
        return TemperatureAlertSeverity.warning
    else:
        return TemperatureAlertSeverity.info


def get_regulatory_impact(severity: str) -> str:
    """Determine regulatory impact based on severity"""
    impacts = {
        TemperatureAlertSeverity.critical: "CRITICAL: Likely violates FDA Cold Chain regulations (21 CFR 211.42). Vaccine potency compromised. Product may require destruction or recall.",
        TemperatureAlertSeverity.warning: "WARNING: Potential FDA compliance issue. Product efficacy may be affected. Requires QA investigation before distribution.",
        TemperatureAlertSeverity.info: "ADVISORY: Minor temperature variance. Meets regulatory minimum but warrants monitoring."
    }
    return impacts.get(severity, "Unknown regulatory impact")
