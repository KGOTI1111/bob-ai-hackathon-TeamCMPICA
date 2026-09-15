"""
Database models for Supply Chain Optimizer
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime


class ShipmentStatus(str, enum.Enum):
    pending = "pending"
    in_transit = "in_transit"
    delayed = "delayed"
    diverted = "diverted"
    delivered = "delivered"
    cancelled = "cancelled"


class TemperatureAlertSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class Shipment(Base):
    """Tracks shipments across supply chain"""
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String(50), unique=True, index=True)
    origin = Column(String(100))
    destination = Column(String(100))
    cargo_description = Column(Text)
    cargo_value = Column(Float)
    is_cold_chain = Column(Boolean, default=False)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.pending)
    current_location = Column(String(100))
    planned_delivery = Column(DateTime)
    estimated_delivery = Column(DateTime)
    actual_delivery = Column(DateTime, nullable=True)
    carrier = Column(String(100))
    container_id = Column(String(50), index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Disruption(Base):
    """Tracks active supply chain disruptions"""
    __tablename__ = "disruptions"

    id = Column(Integer, primary_key=True, index=True)
    disruption_id = Column(String(50), unique=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    disruption_type = Column(String(50))  # weather, strike, geopolitical, etc.
    affected_region = Column(String(100), index=True)
    severity = Column(String(20))  # low, medium, high, critical
    start_time = Column(DateTime)
    estimated_resolution = Column(DateTime)
    affected_shipments_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FleetAsset(Base):
    """Tracks fleet assets (trucks, containers, vessels)"""
    __tablename__ = "fleet_assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(50), unique=True, index=True)
    asset_type = Column(String(50))  # truck, container, vessel
    status = Column(String(20))  # idle, in_transit, maintenance, damaged
    current_location = Column(String(100))
    capacity_tons = Column(Float)
    is_cold_chain_capable = Column(Boolean, default=False)
    current_shipment = Column(String(50), nullable=True)
    available_from = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ColdChainSensor(Base):
    """IoT sensors for cold chain monitoring"""
    __tablename__ = "cold_chain_sensors"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(50), unique=True, index=True)
    shipment_id = Column(String(50), index=True)
    container_id = Column(String(50), index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    temperature = Column(Float)
    humidity = Column(Float, nullable=True)
    timestamp = Column(DateTime, index=True)
    created_at = Column(DateTime, server_default=func.now())


class TemperatureAlert(Base):
    """Temperature excursion alerts and severity classification"""
    __tablename__ = "temperature_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, index=True)
    shipment_id = Column(String(50), index=True)
    sensor_id = Column(String(50))
    temperature_recorded = Column(Float)
    expected_min = Column(Float)
    expected_max = Column(Float)
    duration_minutes = Column(Integer)  # how long out of spec
    severity = Column(Enum(TemperatureAlertSeverity), default=TemperatureAlertSeverity.info)
    regulatory_impact = Column(Text, nullable=True)  # FDA, EU, etc. regulations affected
    timestamp = Column(DateTime)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class RouteRecommendation(Base):
    """Re-routing recommendations for affected shipments"""
    __tablename__ = "route_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String(50), index=True)
    disruption_id = Column(String(50))
    original_route = Column(Text)
    recommended_route = Column(Text)
    alternative_carrier = Column(String(100), nullable=True)
    cost_impact = Column(Float)
    time_impact_hours = Column(Float)
    risk_score = Column(Float)  # 0-100
    implemented = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
