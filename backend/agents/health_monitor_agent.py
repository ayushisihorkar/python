import numpy as np
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from .base_agent import BaseAgent
from database.database import AsyncSessionLocal
from database.models import Vehicle, VehicleTelemetry

class HealthMonitorAgent(BaseAgent):
    """Agent responsible for monitoring vehicle health and detecting anomalies"""
    
    def __init__(self):
        super().__init__("HealthMonitor")
        self.anomaly_thresholds = {
            "battery_soh_critical": 70.0,  # %
            "battery_soh_warning": 80.0,
            "battery_temp_critical": 45.0,  # Celsius
            "battery_temp_warning": 40.0,
            "voltage_imbalance_critical": 0.5,  # V
            "voltage_imbalance_warning": 0.3,
            "motor_temp_critical": 85.0,  # Celsius
            "motor_temp_warning": 75.0,
            "coolant_temp_critical": 95.0,  # Celsius
            "coolant_temp_warning": 85.0,
            "coolant_level_critical": 20.0,  # %
            "coolant_level_warning": 30.0,
            "motor_efficiency_critical": 75.0,  # %
            "motor_efficiency_warning": 80.0,
        }
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process vehicle telemetry data for health monitoring"""
        action_type = data.get("action", "health_check")
        
        if action_type == "health_check":
            return await self._perform_health_check(data.get("vehicle_id"))
        elif action_type == "anomaly_detection":
            return await self._detect_anomalies(data)
        elif action_type == "predictive_analysis":
            return await self._predict_maintenance_needs(data.get("vehicle_id"))
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def _perform_health_check(self, vehicle_id: int) -> Dict[str, Any]:
        """Perform comprehensive health check on a vehicle"""
        async with AsyncSessionLocal() as session:
            # Get vehicle with latest telemetry
            stmt = select(Vehicle).options(
                selectinload(Vehicle.telemetry_data)
            ).where(Vehicle.id == vehicle_id)
            result = await session.execute(stmt)
            vehicle = result.scalar_one_or_none()
            
            if not vehicle:
                return {"error": "Vehicle not found", "confidence": 0.0}
            
            # Get latest telemetry
            latest_telemetry = await self._get_latest_telemetry(session, vehicle_id)
            if not latest_telemetry:
                return {"error": "No telemetry data available", "confidence": 0.0}
            
            # Analyze health metrics
            health_status = await self._analyze_health_metrics(latest_telemetry)
            
            # Get historical trends
            trends = await self._analyze_trends(session, vehicle_id)
            
            # Calculate overall health score
            overall_score = self._calculate_health_score(health_status)
            
            # Determine status and recommendations
            status, recommendations = self._determine_vehicle_status(health_status, trends)
            
            # Update vehicle status if needed
            if vehicle.status != status:
                vehicle.status = status
                await session.commit()
            
            return {
                "vehicle_id": vehicle_id,
                "overall_health_score": overall_score,
                "status": status,
                "health_metrics": health_status,
                "trends": trends,
                "recommendations": recommendations,
                "confidence": self._calculate_confidence({
                    "data_confidence": 0.9 if latest_telemetry else 0.1,
                    "analysis_confidence": 0.85
                }),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _detect_anomalies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in vehicle telemetry data"""
        telemetry = data.get("telemetry", {})
        vehicle_id = data.get("vehicle_id")
        
        anomalies = []
        severity_scores = []
        
        # Check each metric against thresholds
        for metric, value in telemetry.items():
            if value is None:
                continue
                
            anomaly = self._check_metric_anomaly(metric, value)
            if anomaly:
                anomalies.append(anomaly)
                severity_scores.append(anomaly["severity_score"])
        
        # Get historical context for anomalies
        if vehicle_id:
            historical_anomalies = await self._get_historical_anomalies(vehicle_id)
            for anomaly in anomalies:
                anomaly["historical_context"] = historical_anomalies.get(
                    anomaly["metric"], "No historical data"
                )
        
        overall_severity = max(severity_scores) if severity_scores else 0.0
        
        return {
            "vehicle_id": vehicle_id,
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "overall_severity": overall_severity,
            "requires_immediate_attention": overall_severity >= 0.8,
            "confidence": 0.9 if anomalies else 0.7,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _predict_maintenance_needs(self, vehicle_id: int) -> Dict[str, Any]:
        """Predict future maintenance needs based on current trends"""
        async with AsyncSessionLocal() as session:
            # Get historical telemetry data
            historical_data = await self._get_historical_telemetry(session, vehicle_id, days=30)
            
            if len(historical_data) < 10:
                return {
                    "error": "Insufficient historical data for prediction",
                    "confidence": 0.0
                }
            
            predictions = []
            
            # Analyze trends for key metrics
            metrics_to_analyze = [
                "battery_soh", "battery_soc", "charge_cycles",
                "motor_efficiency", "coolant_level"
            ]
            
            for metric in metrics_to_analyze:
                trend_analysis = self._analyze_metric_trend(historical_data, metric)
                if trend_analysis["prediction"]:
                    predictions.append(trend_analysis)
            
            # Generate maintenance recommendations
            recommendations = self._generate_maintenance_recommendations(predictions)
            
            return {
                "vehicle_id": vehicle_id,
                "predictions": predictions,
                "maintenance_recommendations": recommendations,
                "confidence": self._calculate_confidence({
                    "data_confidence": min(1.0, len(historical_data) / 30),
                    "model_confidence": 0.75
                }),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _check_metric_anomaly(self, metric: str, value: float) -> Optional[Dict[str, Any]]:
        """Check if a metric value indicates an anomaly"""
        critical_threshold = self.anomaly_thresholds.get(f"{metric}_critical")
        warning_threshold = self.anomaly_thresholds.get(f"{metric}_warning")
        
        if not critical_threshold and not warning_threshold:
            return None
        
        anomaly = None
        
        # Different logic for different metric types
        if metric in ["battery_soh", "motor_efficiency", "coolant_level"]:
            # Lower values are worse
            if critical_threshold and value < critical_threshold:
                anomaly = {
                    "metric": metric,
                    "value": value,
                    "threshold": critical_threshold,
                    "severity": "critical",
                    "severity_score": 1.0,
                    "message": f"{metric} is critically low: {value}"
                }
            elif warning_threshold and value < warning_threshold:
                anomaly = {
                    "metric": metric,
                    "value": value,
                    "threshold": warning_threshold,
                    "severity": "warning",
                    "severity_score": 0.6,
                    "message": f"{metric} is below normal: {value}"
                }
        else:
            # Higher values are worse
            if critical_threshold and value > critical_threshold:
                anomaly = {
                    "metric": metric,
                    "value": value,
                    "threshold": critical_threshold,
                    "severity": "critical",
                    "severity_score": 1.0,
                    "message": f"{metric} is critically high: {value}"
                }
            elif warning_threshold and value > warning_threshold:
                anomaly = {
                    "metric": metric,
                    "value": value,
                    "threshold": warning_threshold,
                    "severity": "warning",
                    "severity_score": 0.6,
                    "message": f"{metric} is above normal: {value}"
                }
        
        return anomaly
    
    async def _get_latest_telemetry(self, session, vehicle_id: int) -> Optional[VehicleTelemetry]:
        """Get the latest telemetry data for a vehicle"""
        stmt = select(VehicleTelemetry).where(
            VehicleTelemetry.vehicle_id == vehicle_id
        ).order_by(VehicleTelemetry.timestamp.desc()).limit(1)
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_historical_telemetry(self, session, vehicle_id: int, days: int = 30) -> List[VehicleTelemetry]:
        """Get historical telemetry data for trend analysis"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(VehicleTelemetry).where(
            and_(
                VehicleTelemetry.vehicle_id == vehicle_id,
                VehicleTelemetry.timestamp >= cutoff_date
            )
        ).order_by(VehicleTelemetry.timestamp.desc())
        
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def _analyze_health_metrics(self, telemetry: VehicleTelemetry) -> Dict[str, Any]:
        """Analyze individual health metrics"""
        metrics = {}
        
        if telemetry.battery_soh is not None:
            metrics["battery_health"] = {
                "value": telemetry.battery_soh,
                "status": self._get_metric_status("battery_soh", telemetry.battery_soh),
                "metric": "battery_soh"
            }
        
        if telemetry.battery_temp is not None:
            metrics["battery_temperature"] = {
                "value": telemetry.battery_temp,
                "status": self._get_metric_status("battery_temp", telemetry.battery_temp),
                "metric": "battery_temp"
            }
        
        if telemetry.motor_efficiency is not None:
            metrics["motor_efficiency"] = {
                "value": telemetry.motor_efficiency,
                "status": self._get_metric_status("motor_efficiency", telemetry.motor_efficiency),
                "metric": "motor_efficiency"
            }
        
        if telemetry.coolant_level is not None:
            metrics["coolant_system"] = {
                "value": telemetry.coolant_level,
                "status": self._get_metric_status("coolant_level", telemetry.coolant_level),
                "metric": "coolant_level"
            }
        
        return metrics
    
    def _get_metric_status(self, metric: str, value: float) -> str:
        """Get status (good/warning/critical) for a metric value"""
        critical_threshold = self.anomaly_thresholds.get(f"{metric}_critical")
        warning_threshold = self.anomaly_thresholds.get(f"{metric}_warning")
        
        if not critical_threshold and not warning_threshold:
            return "unknown"
        
        if metric in ["battery_soh", "motor_efficiency", "coolant_level"]:
            # Lower values are worse
            if critical_threshold and value < critical_threshold:
                return "critical"
            elif warning_threshold and value < warning_threshold:
                return "warning"
            else:
                return "good"
        else:
            # Higher values are worse
            if critical_threshold and value > critical_threshold:
                return "critical"
            elif warning_threshold and value > warning_threshold:
                return "warning"
            else:
                return "good"
    
    async def _analyze_trends(self, session, vehicle_id: int) -> Dict[str, Any]:
        """Analyze trends in vehicle health metrics"""
        historical_data = await self._get_historical_telemetry(session, vehicle_id, days=7)
        
        if len(historical_data) < 3:
            return {"error": "Insufficient data for trend analysis"}
        
        trends = {}
        
        # Analyze battery health trend
        battery_soh_values = [t.battery_soh for t in historical_data if t.battery_soh is not None]
        if len(battery_soh_values) >= 3:
            trend = self._calculate_trend(battery_soh_values)
            trends["battery_soh"] = {
                "direction": trend["direction"],
                "rate": trend["rate"],
                "confidence": trend["confidence"]
            }
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and rate for a series of values"""
        if len(values) < 2:
            return {"direction": "stable", "rate": 0.0, "confidence": 0.0}
        
        # Simple linear regression
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Determine direction and confidence
        if abs(slope) < 0.1:
            direction = "stable"
        elif slope > 0:
            direction = "improving"
        else:
            direction = "declining"
        
        # Calculate R-squared for confidence
        y_pred = np.poly1d(np.polyfit(x, y, 1))(x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            "direction": direction,
            "rate": abs(slope),
            "confidence": max(0.0, min(1.0, r_squared))
        }
    
    def _calculate_health_score(self, health_metrics: Dict[str, Any]) -> float:
        """Calculate overall health score from individual metrics"""
        if not health_metrics:
            return 0.0
        
        scores = []
        weights = {
            "battery_health": 0.3,
            "motor_efficiency": 0.25,
            "coolant_system": 0.2,
            "battery_temperature": 0.25
        }
        
        for metric_name, metric_data in health_metrics.items():
            status = metric_data.get("status", "unknown")
            weight = weights.get(metric_name, 0.1)
            
            if status == "good":
                score = 1.0
            elif status == "warning":
                score = 0.6
            elif status == "critical":
                score = 0.2
            else:
                score = 0.5
            
            scores.append(score * weight)
        
        return sum(scores) / sum(weights.values()) if health_metrics else 0.0
    
    def _determine_vehicle_status(self, health_metrics: Dict[str, Any], trends: Dict[str, Any]) -> tuple:
        """Determine overall vehicle status and recommendations"""
        statuses = [metric.get("status", "unknown") for metric in health_metrics.values()]
        
        if "critical" in statuses:
            status = "critical"
            recommendations = [
                "Immediate inspection required",
                "Schedule emergency maintenance",
                "Consider taking vehicle out of service"
            ]
        elif "warning" in statuses:
            status = "warning"
            recommendations = [
                "Schedule preventive maintenance",
                "Monitor closely",
                "Check affected systems"
            ]
        else:
            status = "operational"
            recommendations = [
                "Continue normal operations",
                "Regular maintenance schedule"
            ]
        
        return status, recommendations
    
    def _analyze_metric_trend(self, historical_data: List[VehicleTelemetry], metric: str) -> Dict[str, Any]:
        """Analyze trend for a specific metric"""
        values = []
        for data in historical_data:
            value = getattr(data, metric, None)
            if value is not None:
                values.append(value)
        
        if len(values) < 3:
            return {"metric": metric, "prediction": None, "confidence": 0.0}
        
        trend = self._calculate_trend(values)
        
        # Predict when metric might reach critical threshold
        prediction = None
        if trend["direction"] == "declining" and trend["rate"] > 0:
            critical_threshold = self.anomaly_thresholds.get(f"{metric}_critical")
            if critical_threshold and values[0] > critical_threshold:
                days_to_critical = (values[0] - critical_threshold) / trend["rate"]
                if days_to_critical > 0:
                    prediction = {
                        "days_to_critical": days_to_critical,
                        "predicted_date": (datetime.utcnow() + timedelta(days=days_to_critical)).isoformat(),
                        "current_value": values[0],
                        "critical_threshold": critical_threshold
                    }
        
        return {
            "metric": metric,
            "trend": trend,
            "prediction": prediction,
            "confidence": trend["confidence"]
        }
    
    def _generate_maintenance_recommendations(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate maintenance recommendations based on predictions"""
        recommendations = []
        
        for prediction in predictions:
            if prediction.get("prediction"):
                pred_data = prediction["prediction"]
                days_to_critical = pred_data.get("days_to_critical", 0)
                
                if days_to_critical <= 7:
                    priority = "urgent"
                    action = "Schedule immediate maintenance"
                elif days_to_critical <= 30:
                    priority = "high"
                    action = "Schedule maintenance within 2 weeks"
                else:
                    priority = "normal"
                    action = "Monitor and schedule routine maintenance"
                
                recommendations.append({
                    "metric": prediction["metric"],
                    "priority": priority,
                    "action": action,
                    "estimated_days": days_to_critical,
                    "confidence": prediction["confidence"]
                })
        
        return sorted(recommendations, key=lambda x: x["estimated_days"])
    
    async def _get_historical_anomalies(self, vehicle_id: int) -> Dict[str, str]:
        """Get historical context for anomalies"""
        # This would typically query historical anomaly data
        # For now, return placeholder data
        return {
            "battery_soh": "Similar issue detected 2 months ago",
            "battery_temp": "Temperature spikes observed during summer months",
            "motor_efficiency": "Gradual decline over past 6 months"
        }