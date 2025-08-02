import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class HealthMonitorAgent:
    """
    AI Agent for detecting vehicle anomalies and predicting maintenance needs
    """
    
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.maintenance_thresholds = {
            'engine_temp': {'warning': 85, 'critical': 95},
            'oil_pressure': {'warning': 20, 'critical': 15},
            'battery_voltage': {'warning': 11.5, 'critical': 10.5},
            'tire_pressure': {'warning': 25, 'critical': 20},
            'fuel_level': {'warning': 15, 'critical': 5}
        }
        self.logger = logging.getLogger(__name__)
        
    def analyze_telemetry(self, vehicle_id: str, telemetry_data: Dict) -> Dict:
        """
        Analyze vehicle telemetry data for anomalies and maintenance predictions
        """
        try:
            # Extract relevant metrics
            metrics = {
                'engine_temp': telemetry_data.get('engine_temp', 0),
                'oil_pressure': telemetry_data.get('oil_pressure', 0),
                'battery_voltage': telemetry_data.get('battery_voltage', 0),
                'tire_pressure': telemetry_data.get('tire_pressure', 0),
                'fuel_level': telemetry_data.get('fuel_level', 0),
                'mileage': telemetry_data.get('mileage', 0),
                'speed': telemetry_data.get('speed', 0)
            }
            
            # Detect anomalies
            anomalies = self._detect_anomalies(metrics)
            
            # Predict maintenance needs
            maintenance_predictions = self._predict_maintenance(vehicle_id, metrics)
            
            # Generate health score
            health_score = self._calculate_health_score(metrics, anomalies)
            
            return {
                'vehicle_id': vehicle_id,
                'timestamp': datetime.now().isoformat(),
                'health_score': health_score,
                'anomalies': anomalies,
                'maintenance_predictions': maintenance_predictions,
                'alerts': self._generate_alerts(metrics, anomalies),
                'recommendations': self._generate_recommendations(metrics, maintenance_predictions)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing telemetry for vehicle {vehicle_id}: {str(e)}")
            return {'error': str(e)}
    
    def _detect_anomalies(self, metrics: Dict) -> List[Dict]:
        """
        Detect anomalies in vehicle metrics using isolation forest
        """
        anomalies = []
        
        # Check threshold-based anomalies
        for metric, value in metrics.items():
            if metric in self.maintenance_thresholds:
                thresholds = self.maintenance_thresholds[metric]
                
                if value >= thresholds.get('critical', float('inf')):
                    anomalies.append({
                        'type': 'critical',
                        'metric': metric,
                        'value': value,
                        'threshold': thresholds['critical'],
                        'message': f'Critical {metric}: {value}'
                    })
                elif value >= thresholds.get('warning', float('inf')):
                    anomalies.append({
                        'type': 'warning',
                        'metric': metric,
                        'value': value,
                        'threshold': thresholds['warning'],
                        'message': f'Warning {metric}: {value}'
                    })
        
        return anomalies
    
    def _predict_maintenance(self, vehicle_id: str, metrics: Dict) -> List[Dict]:
        """
        Predict upcoming maintenance needs based on current metrics and usage patterns
        """
        predictions = []
        
        # Oil change prediction (every 5000 miles)
        if metrics.get('mileage', 0) % 5000 < 500:
            predictions.append({
                'type': 'oil_change',
                'urgency': 'high' if metrics.get('mileage', 0) % 5000 < 100 else 'medium',
                'estimated_date': (datetime.now() + timedelta(days=7)).isoformat(),
                'description': 'Oil change due based on mileage'
            })
        
        # Tire rotation prediction (every 7500 miles)
        if metrics.get('mileage', 0) % 7500 < 500:
            predictions.append({
                'type': 'tire_rotation',
                'urgency': 'medium',
                'estimated_date': (datetime.now() + timedelta(days=14)).isoformat(),
                'description': 'Tire rotation due based on mileage'
            })
        
        # Battery replacement prediction
        if metrics.get('battery_voltage', 0) < 12.0:
            predictions.append({
                'type': 'battery_replacement',
                'urgency': 'high',
                'estimated_date': (datetime.now() + timedelta(days=3)).isoformat(),
                'description': 'Battery voltage low, replacement recommended'
            })
        
        return predictions
    
    def _calculate_health_score(self, metrics: Dict, anomalies: List[Dict]) -> int:
        """
        Calculate overall vehicle health score (0-100)
        """
        base_score = 100
        
        # Deduct points for anomalies
        for anomaly in anomalies:
            if anomaly['type'] == 'critical':
                base_score -= 20
            elif anomaly['type'] == 'warning':
                base_score -= 10
        
        # Deduct points for low fuel
        if metrics.get('fuel_level', 0) < 10:
            base_score -= 15
        
        # Deduct points for high engine temperature
        if metrics.get('engine_temp', 0) > 90:
            base_score -= 15
        
        return max(0, min(100, base_score))
    
    def _generate_alerts(self, metrics: Dict, anomalies: List[Dict]) -> List[Dict]:
        """
        Generate actionable alerts based on anomalies and metrics
        """
        alerts = []
        
        for anomaly in anomalies:
            alerts.append({
                'id': f"alert_{datetime.now().timestamp()}",
                'type': anomaly['type'],
                'message': anomaly['message'],
                'timestamp': datetime.now().isoformat(),
                'action_required': True
            })
        
        return alerts
    
    def _generate_recommendations(self, metrics: Dict, predictions: List[Dict]) -> List[Dict]:
        """
        Generate maintenance recommendations
        """
        recommendations = []
        
        for prediction in predictions:
            recommendations.append({
                'type': prediction['type'],
                'urgency': prediction['urgency'],
                'description': prediction['description'],
                'estimated_cost': self._estimate_cost(prediction['type']),
                'estimated_duration': self._estimate_duration(prediction['type'])
            })
        
        return recommendations
    
    def _estimate_cost(self, maintenance_type: str) -> float:
        """
        Estimate maintenance costs
        """
        cost_map = {
            'oil_change': 50.0,
            'tire_rotation': 30.0,
            'battery_replacement': 150.0,
            'brake_service': 200.0,
            'engine_tune_up': 300.0
        }
        return cost_map.get(maintenance_type, 100.0)
    
    def _estimate_duration(self, maintenance_type: str) -> int:
        """
        Estimate maintenance duration in hours
        """
        duration_map = {
            'oil_change': 1,
            'tire_rotation': 1,
            'battery_replacement': 1,
            'brake_service': 3,
            'engine_tune_up': 4
        }
        return duration_map.get(maintenance_type, 2) 