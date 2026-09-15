"""
API routes for disruption management and affected shipment identification
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.database import get_db
from app.models import Disruption, Shipment, ShipmentStatus, RouteRecommendation
from app.schemas import (
    DisruptionCreate, Disruption as DisruptionSchema,
    Shipment as ShipmentSchema, RouteRecommendation as RouteRecommendationSchema,
    DisruptionSummary
)
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/disruptions", tags=["disruptions"])


@router.get("/", response_model=List[DisruptionSchema])
def list_disruptions(
    db: Session = Depends(get_db),
    is_active: bool = Query(None),
    severity: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """List all disruptions with optional filtering"""
    query = db.query(Disruption)
    
    if is_active is not None:
        query = query.filter(Disruption.is_active == is_active)
    if severity:
        query = query.filter(Disruption.severity == severity)
    
    return query.order_by(desc(Disruption.created_at)).offset(skip).limit(limit).all()


@router.get("/{disruption_id}", response_model=DisruptionSchema)
def get_disruption(disruption_id: str, db: Session = Depends(get_db)):
    """Get detailed disruption information"""
    disruption = db.query(Disruption).filter(Disruption.disruption_id == disruption_id).first()
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")
    return disruption


@router.post("/", response_model=DisruptionSchema)
def create_disruption(disruption: DisruptionCreate, db: Session = Depends(get_db)):
    """Create a new disruption and identify affected shipments"""
    db_disruption = Disruption(**disruption.dict())
    db.add(db_disruption)
    db.commit()
    
    # Find and count affected shipments
    affected_shipments = db.query(Shipment).filter(
        and_(
            Shipment.is_cold_chain == True or Shipment.status == ShipmentStatus.in_transit,
            (Shipment.current_location == disruption.affected_region) |
            (Shipment.destination == disruption.affected_region)
        )
    ).all()
    
    db_disruption.affected_shipments_count = len(affected_shipments)
    db.add(db_disruption)
    db.commit()
    db.refresh(db_disruption)
    
    return db_disruption


@router.get("/{disruption_id}/affected-shipments", response_model=List[ShipmentSchema])
def get_affected_shipments(
    disruption_id: str,
    db: Session = Depends(get_db),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """Get all shipments affected by a disruption"""
    disruption = db.query(Disruption).filter(Disruption.disruption_id == disruption_id).first()
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")
    
    affected = db.query(Shipment).filter(
        (Shipment.current_location == disruption.affected_region) |
        (Shipment.destination == disruption.affected_region),
        Shipment.status.in_([ShipmentStatus.pending, ShipmentStatus.in_transit])
    ).offset(skip).limit(limit).all()
    
    return affected


@router.get("/{disruption_id}/recommendations", response_model=List[RouteRecommendationSchema])
def get_route_recommendations(
    disruption_id: str,
    db: Session = Depends(get_db)
):
    """Get route recommendations for affected shipments"""
    recommendations = db.query(RouteRecommendation).filter(
        RouteRecommendation.disruption_id == disruption_id
    ).all()
    return recommendations


@router.post("/{disruption_id}/recommendations")
def create_route_recommendation(
    disruption_id: str,
    recommendation_data: dict,
    db: Session = Depends(get_db)
):
    """Generate or create route recommendation for a shipment"""
    disruption = db.query(Disruption).filter(Disruption.disruption_id == disruption_id).first()
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")
    
    rec = RouteRecommendation(
        disruption_id=disruption_id,
        **recommendation_data
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.patch("/{disruption_id}/resolve")
def resolve_disruption(disruption_id: str, db: Session = Depends(get_db)):
    """Mark disruption as resolved"""
    disruption = db.query(Disruption).filter(Disruption.disruption_id == disruption_id).first()
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")
    
    disruption.is_active = False
    disruption.estimated_resolution = datetime.utcnow()
    db.add(disruption)
    db.commit()
    db.refresh(disruption)
    return disruption


@router.get("/summary/dashboard", response_model=DisruptionSummary)
def get_disruption_summary(db: Session = Depends(get_db)):
    """Get summary statistics for disruptions"""
    active = db.query(Disruption).filter(Disruption.is_active == True).all()
    total_affected = sum(d.affected_shipments_count for d in active)
    critical = len([d for d in active if d.severity == "critical"])
    regions = list(set(d.affected_region for d in active))
    
    return DisruptionSummary(
        active_disruptions=len(active),
        total_affected_shipments=total_affected,
        critical_disruptions=critical,
        regions_affected=regions
    )
