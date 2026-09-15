"""
API routes for fleet asset management and redeployment
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import FleetAsset
from app.schemas import FleetAssetCreate, FleetAsset as FleetAssetSchema, FleetSummary
from typing import List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/fleet", tags=["fleet"])


@router.get("/", response_model=List[FleetAssetSchema])
def list_fleet_assets(
    db: Session = Depends(get_db),
    status: str = Query(None),
    asset_type: str = Query(None),
    is_available: bool = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """List all fleet assets with filtering"""
    query = db.query(FleetAsset)
    
    if status:
        query = query.filter(FleetAsset.status == status)
    if asset_type:
        query = query.filter(FleetAsset.asset_type == asset_type)
    if is_available is not None:
        query = query.filter(
            FleetAsset.status == "idle",
            FleetAsset.available_from <= datetime.utcnow()
        )
    
    return query.order_by(desc(FleetAsset.updated_at)).offset(skip).limit(limit).all()


@router.get("/{asset_id}", response_model=FleetAssetSchema)
def get_fleet_asset(asset_id: str, db: Session = Depends(get_db)):
    """Get detailed fleet asset information"""
    asset = db.query(FleetAsset).filter(FleetAsset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Fleet asset not found")
    return asset


@router.post("/", response_model=FleetAssetSchema)
def create_fleet_asset(asset: FleetAssetCreate, db: Session = Depends(get_db)):
    """Register a new fleet asset"""
    db_asset = FleetAsset(**asset.dict())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.patch("/{asset_id}", response_model=FleetAssetSchema)
def update_fleet_asset(
    asset_id: str,
    asset_update: dict,
    db: Session = Depends(get_db)
):
    """Update fleet asset status or location"""
    db_asset = db.query(FleetAsset).filter(FleetAsset.asset_id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Fleet asset not found")
    
    for field, value in asset_update.items():
        if field in ["status", "current_location", "current_shipment", "available_from"]:
            setattr(db_asset, field, value)
    
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.get("/available/candidates", response_model=List[FleetAssetSchema])
def get_available_assets(
    asset_type: str = Query(None),
    is_cold_chain: bool = Query(None),
    min_capacity: float = Query(None),
    location: str = Query(None)
):
    """Find available assets for redeployment"""
    db: Session = Depends(get_db)
    
    query = db.query(FleetAsset).filter(
        FleetAsset.status == "idle",
        FleetAsset.available_from <= datetime.utcnow()
    )
    
    if asset_type:
        query = query.filter(FleetAsset.asset_type == asset_type)
    if is_cold_chain is not None:
        query = query.filter(FleetAsset.is_cold_chain_capable == is_cold_chain)
    if min_capacity:
        query = query.filter(FleetAsset.capacity_tons >= min_capacity)
    if location:
        query = query.filter(FleetAsset.current_location == location)
    
    return query.all()


@router.post("/{asset_id}/deploy")
def deploy_asset(
    asset_id: str,
    deployment: dict,
    db: Session = Depends(get_db)
):
    """Deploy an idle asset to a new shipment"""
    db_asset = db.query(FleetAsset).filter(FleetAsset.asset_id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Fleet asset not found")
    
    if db_asset.status != "idle":
        raise HTTPException(status_code=400, detail="Asset is not available")
    
    db_asset.status = "in_transit"
    db_asset.current_shipment = deployment.get("shipment_id")
    db_asset.current_location = deployment.get("location")
    
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return {
        "message": "Asset deployed successfully",
        "asset": db_asset
    }


@router.post("/{asset_id}/return")
def return_asset(
    asset_id: str,
    db: Session = Depends(get_db)
):
    """Return an asset to idle status"""
    db_asset = db.query(FleetAsset).filter(FleetAsset.asset_id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Fleet asset not found")
    
    db_asset.status = "idle"
    db_asset.current_shipment = None
    db_asset.available_from = datetime.utcnow()
    
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return {"message": "Asset returned to idle", "asset": db_asset}


@router.get("/summary/dashboard", response_model=FleetSummary)
def get_fleet_summary(db: Session = Depends(get_db)):
    """Get fleet summary statistics"""
    total = db.query(FleetAsset).count()
    idle = db.query(FleetAsset).filter(FleetAsset.status == "idle").count()
    in_transit = db.query(FleetAsset).filter(FleetAsset.status == "in_transit").count()
    maintenance = db.query(FleetAsset).filter(FleetAsset.status == "maintenance").count()
    cold_chain = db.query(FleetAsset).filter(FleetAsset.is_cold_chain_capable == True).count()
    
    return FleetSummary(
        total_assets=total,
        idle_assets=idle,
        in_transit=in_transit,
        maintenance=maintenance,
        cold_chain_capable=cold_chain
    )
