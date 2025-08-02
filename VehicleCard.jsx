import React, { useState, useEffect } from 'react';
import { 
  Car, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Wrench, 
  Fuel, 
  Gauge, 
  MapPin,
  Clock,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';

const VehicleCard = ({ vehicle, onViewDetails, onScheduleMaintenance }) => {
  const [telemetry, setTelemetry] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVehicleData = async () => {
      try {
        // In a real app, you would fetch this data from the API
        // For now, we'll simulate the data
        setTelemetry({
          engine_temp: 85.5,
          oil_pressure: 45.2,
          battery_voltage: 12.8,
          tire_pressure: 32.0,
          fuel_level: vehicle.fuel_level || 75.5,
          speed: 35.0,
          timestamp: new Date().toISOString()
        });

        setHealthData({
          health_score: vehicle.health_score || 85,
          anomalies: [],
          alerts: [],
          maintenance_predictions: []
        });

        setLoading(false);
      } catch (error) {
        console.error('Error fetching vehicle data:', error);
        setLoading(false);
      }
    };

    fetchVehicleData();
  }, [vehicle]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'out_of_service':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'rented':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getHealthColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHealthIcon = (score) => {
    if (score >= 80) return <CheckCircle className="w-4 h-4" />;
    if (score >= 60) return <AlertTriangle className="w-4 h-4" />;
    return <XCircle className="w-4 h-4" />;
  };

  const getFuelColor = (level) => {
    if (level >= 50) return 'text-green-600';
    if (level >= 25) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-md p-6 animate-pulse"
      >
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-2/3"></div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-all duration-200"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Car className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {vehicle.make} {vehicle.model}
            </h3>
            <p className="text-sm text-gray-500">{vehicle.license_plate}</p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(vehicle.status)}`}>
          {vehicle.status.replace('_', ' ').toUpperCase()}
        </div>
      </div>

      {/* Vehicle Info */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center space-x-2">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">{vehicle.location}</span>
        </div>
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {vehicle.last_maintenance ? format(new Date(vehicle.last_maintenance), 'MMM dd') : 'N/A'}
          </span>
        </div>
      </div>

      {/* Health Score */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Health Score</span>
          <div className={`flex items-center space-x-1 ${getHealthColor(healthData?.health_score)}`}>
            {getHealthIcon(healthData?.health_score)}
            <span className="text-sm font-semibold">{healthData?.health_score || 0}%</span>
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              healthData?.health_score >= 80 ? 'bg-green-500' :
              healthData?.health_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${healthData?.health_score || 0}%` }}
          ></div>
        </div>
      </div>

      {/* Telemetry Data */}
      {telemetry && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="flex items-center space-x-2">
            <Gauge className="w-4 h-4 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Engine Temp</p>
              <p className="text-sm font-medium">
                {telemetry.engine_temp}°C
                {telemetry.engine_temp > 90 && <TrendingUp className="w-3 h-3 text-red-500 inline ml-1" />}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Fuel className="w-4 h-4 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Fuel Level</p>
              <p className={`text-sm font-medium ${getFuelColor(telemetry.fuel_level)}`}>
                {telemetry.fuel_level}%
                {telemetry.fuel_level < 25 && <TrendingDown className="w-3 h-3 text-red-500 inline ml-1" />}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Alerts */}
      {healthData?.alerts && healthData.alerts.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <span className="text-sm font-medium text-red-700">Alerts</span>
          </div>
          <div className="space-y-1">
            {healthData.alerts.slice(0, 2).map((alert, index) => (
              <div key={index} className="text-xs text-red-600 bg-red-50 p-2 rounded">
                {alert.message}
              </div>
            ))}
            {healthData.alerts.length > 2 && (
              <div className="text-xs text-gray-500">
                +{healthData.alerts.length - 2} more alerts
              </div>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-2">
        <button
          onClick={() => onViewDetails(vehicle)}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          View Details
        </button>
        {vehicle.status === 'active' && (
          <button
            onClick={() => onScheduleMaintenance(vehicle)}
            className="flex items-center space-x-1 bg-yellow-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-yellow-700 transition-colors"
          >
            <Wrench className="w-4 h-4" />
            <span>Maintenance</span>
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default VehicleCard; 