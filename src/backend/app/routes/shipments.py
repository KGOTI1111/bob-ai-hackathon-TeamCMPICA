"""
API routes for shipment management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Shipment, Disruption, ShipmentStatus, TemperatureAlert
from app.schemas import ShipmentCreate, ShipmentUpdate, Shipment as ShipmentSchema, ShipmentSummary
from typing import List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


@router.get("/", response_model=List[ShipmentSchema])
def list_shipments(
    db: Session = Depends(get_db),
    status: str = Query(None),
    is_cold_chain: bool = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """List all shipments with optional filtering"""
    query = db.query(Shipment)
    
    if status:
        query = query.filter(Shipment.status == status)
    if is_cold_chain is not None:
        query = query.filter(Shipment.is_cold_chain == is_cold_chain)
    
    return query.order_by(desc(Shipment.created_at)).offset(skip).limit(limit).all()


@router.get("/{shipment_id}", response_model=ShipmentSchema)
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    """Get detailed shipment information"""
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.post("/", response_model=ShipmentSchema)
def create_shipment(shipment: ShipmentCreate, db: Session = Depends(get_db)):
    """Create a new shipment"""
    db_shipment = Shipment(**shipment.dict())
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment


@router.patch("/{shipment_id}", response_model=ShipmentSchema)
def update_shipment(
    shipment_id: str,
    shipment_update: ShipmentUpdate,
    db: Session = Depends(get_db)
):
    """Update shipment status and location"""
    db_shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not db_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    update_data = shipment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_shipment, field, value)
    
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment


@router.get("/{shipment_id}/affected-by", response_model=List[str])
def get_shipment_disruptions(shipment_id: str, db: Session = Depends(get_db)):
    """Get disruptions affecting a specific shipment"""
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Find disruptions in the shipment's affected region
    disruptions = db.query(Disruption).filter(
        Disruption.affected_region == shipment.current_location or 
        Disruption.affected_region == shipment.destination,
        Disruption.is_active == True
    ).all()
    
    return [d.disruption_id for d in disruptions]


@router.get("/summary/dashboard", response_model=ShipmentSummary)
def get_shipment_summary(db: Session = Depends(get_db)):
    """Get summary statistics for dashboard"""
    total = db.query(Shipment).count()
    in_transit = db.query(Shipment).filter(Shipment.status == ShipmentStatus.in_transit).count()
    delayed = db.query(Shipment).filter(Shipment.status == ShipmentStatus.delayed).count()
    delivered = db.query(Shipment).filter(Shipment.status == ShipmentStatus.delivered).count()
    cold_chain = db.query(Shipment).filter(Shipment.is_cold_chain == True).count()
    
    # High risk = cold chain with temperature alerts
    high_risk = db.query(Shipment).filter(
        Shipment.is_cold_chain == True,
        Shipment.id.in_(
            db.query(TemperatureAlert.id).distinct()
        )
    ).count()
    
    return ShipmentSummary(
        total_shipments=total,
        in_transit=in_transit,
        delayed=delayed,
        delivered=delivered,
        cold_chain_shipments=cold_chain,
        high_risk_shipments=high_risk
    )


@router.get("/{shipment_id}/temperature-history")
def get_temperature_history(shipment_id: str, db: Session = Depends(get_db)):
    """Get temperature readings for a cold chain shipment"""
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment or not shipment.is_cold_chain:
        raise HTTPException(status_code=404, detail="Cold chain shipment not found")
    
    alerts = db.query(TemperatureAlert).filter(
        TemperatureAlert.shipment_id == shipment_id
    ).order_by(desc(TemperatureAlert.timestamp)).all()
    
    return alerts
