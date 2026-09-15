"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ShipmentStatusEnum(str, Enum):
    pending = "pending"
    in_transit = "in_transit"
    delayed = "delayed"
    diverted = "diverted"
    delivered = "delivered"
    cancelled = "cancelled"


class ShipmentBase(BaseModel):
    shipment_id: str
    origin: str
    destination: str
    cargo_description: str
    cargo_value: float
    is_cold_chain: bool = False
    carrier: str
    container_id: str
    planned_delivery: datetime


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    status: Optional[ShipmentStatusEnum] = None
    current_location: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None


class Shipment(ShipmentBase):
    id: int
    status: ShipmentStatusEnum
    current_location: Optional[str]
    estimated_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DisruptionBase(BaseModel):
    title: str
    description: str
    disruption_type: str
    affected_region: str
    severity: str
    start_time: datetime
    estimated_resolution: datetime


class DisruptionCreate(DisruptionBase):
    pass


class Disruption(DisruptionBase):
    id: int
    disruption_id: str
    affected_shipments_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FleetAssetBase(BaseModel):
    asset_id: str
    asset_type: str
    status: str
    current_location: str
    capacity_tons: float
    is_cold_chain_capable: bool = False


class FleetAssetCreate(FleetAssetBase):
    pass


class FleetAsset(FleetAssetBase):
    id: int
    current_shipment: Optional[str]
    available_from: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ColdChainSensorBase(BaseModel):
    sensor_id: str
    shipment_id: str
    container_id: str
    temperature: float
    humidity: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ColdChainSensorCreate(ColdChainSensorBase):
    timestamp: datetime


class ColdChainSensor(ColdChainSensorBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TemperatureAlertBase(BaseModel):
    shipment_id: str
    sensor_id: str
    temperature_recorded: float
    expected_min: float
    expected_max: float
    duration_minutes: int


class TemperatureAlertCreate(TemperatureAlertBase):
    timestamp: datetime


class TemperatureAlert(TemperatureAlertBase):
    id: int
    alert_id: str
    severity: str
    regulatory_impact: Optional[str]
    acknowledged: bool
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class RouteRecommendationBase(BaseModel):
    shipment_id: str
    disruption_id: str
    original_route: str
    recommended_route: str
    alternative_carrier: Optional[str]
    cost_impact: float
    time_impact_hours: float
    risk_score: float


class RouteRecommendationCreate(RouteRecommendationBase):
    pass


class RouteRecommendation(RouteRecommendationBase):
    id: int
    implemented: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ShipmentSummary(BaseModel):
    total_shipments: int
    in_transit: int
    delayed: int
    delivered: int
    cold_chain_shipments: int
    high_risk_shipments: int


class DisruptionSummary(BaseModel):
    active_disruptions: int
    total_affected_shipments: int
    critical_disruptions: int
    regions_affected: List[str]


class FleetSummary(BaseModel):
    total_assets: int
    idle_assets: int
    in_transit: int
    maintenance: int
    cold_chain_capable: int
