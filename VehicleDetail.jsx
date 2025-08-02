import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Car, 
  MapPin, 
  Clock, 
  Gauge, 
  Fuel, 
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Wrench,
  Calendar,
  BarChart3
} from 'lucide-react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';

const VehicleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState(null);
  const [telemetry, setTelemetry] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [maintenanceHistory, setMaintenanceHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVehicleData = async () => {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock vehicle data
        const vehicleData = {
          id: id,
          make: 'Toyota',
          model: 'Camry',
          year: 2022,
          license_plate: 'ABC123',
          status: 'active',
          location: 'Downtown Garage',
          health_score: 85,
          last_maintenance: '2024-01-15T10:00:00Z',
          mileage: 45000,
          fuel_level: 75.5
        };

        const telemetryData = {
          engine_temp: 85.5,
          oil_pressure: 45.2,
          battery_voltage: 12.8,
          tire_pressure: 32.0,
          fuel_level: 75.5,
          speed: 35.0,
          latitude: 40.7128,
          longitude: -74.0060,
          timestamp: new Date().toISOString()
        };

        const healthAnalysis = {
          health_score: 85,
          anomalies: [],
          alerts: [],
          maintenance_predictions: [
            {
              type: 'oil_change',
              urgency: 'medium',
              estimated_date: '2024-02-15T00:00:00Z',
              description: 'Oil change due in 3 weeks'
            }
          ],
          recommendations: [
            {
              type: 'tire_rotation',
              urgency: 'low',
              description: 'Tire rotation recommended',
              estimated_cost: 30.0,
              estimated_duration: 1
            }
          ]
        };

        const maintenanceHistoryData = [
          {
            id: 1,
            task_type: 'oil_change',
            description: 'Regular oil change service',
            performed_by: 'Premium Auto Service',
            cost: 50.0,
            duration_hours: 1,
            timestamp: '2024-01-15T10:00:00Z',
            status: 'completed'
          },
          {
            id: 2,
            task_type: 'tire_rotation',
            description: 'Tire rotation and balance',
            performed_by: 'Quick Fix Garage',
            cost: 30.0,
            duration_hours: 1,
            timestamp: '2024-01-10T14:30:00Z',
            status: 'completed'
          }
        ];

        setVehicle(vehicleData);
        setTelemetry(telemetryData);
        setHealthData(healthAnalysis);
        setMaintenanceHistory(maintenanceHistoryData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching vehicle data:', error);
        setLoading(false);
      }
    };

    fetchVehicleData();
  }, [id]);

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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading vehicle details...</p>
        </div>
      </div>
    );
  }

  if (!vehicle) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Car className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Vehicle not found</h3>
          <p className="text-gray-600">The vehicle you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Dashboard</span>
              </button>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(vehicle.status)}`}>
                {vehicle.status.replace('_', ' ').toUpperCase()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Vehicle Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow p-6 mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Car className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  {vehicle.make} {vehicle.model}
                </h1>
                <p className="text-gray-600">{vehicle.license_plate} • {vehicle.year}</p>
              </div>
            </div>
            <div className="text-right">
              <div className={`flex items-center space-x-2 ${getHealthColor(vehicle.health_score)}`}>
                <CheckCircle className="w-5 h-5" />
                <span className="text-2xl font-bold">{vehicle.health_score}%</span>
              </div>
              <p className="text-sm text-gray-600">Health Score</p>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Telemetry Data */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-lg shadow p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Live Telemetry</h2>
              {telemetry && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      <Gauge className="w-5 h-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-600">Engine Temp</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {telemetry.engine_temp}°C
                      {telemetry.engine_temp > 90 && <TrendingUp className="w-4 h-4 text-red-500 inline ml-1" />}
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      <Fuel className="w-5 h-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-600">Fuel Level</span>
                    </div>
                    <p className={`text-2xl font-bold ${telemetry.fuel_level < 25 ? 'text-red-600' : 'text-gray-900'}`}>
                      {telemetry.fuel_level}%
                      {telemetry.fuel_level < 25 && <TrendingDown className="w-4 h-4 text-red-500 inline ml-1" />}
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      <BarChart3 className="w-5 h-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-600">Oil Pressure</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{telemetry.oil_pressure} PSI</p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      <Clock className="w-5 h-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-600">Speed</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{telemetry.speed} mph</p>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Maintenance History */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-lg shadow p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Maintenance History</h2>
              <div className="space-y-4">
                {maintenanceHistory.map((maintenance) => (
                  <div key={maintenance.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900 capitalize">
                          {maintenance.task_type.replace('_', ' ')}
                        </h3>
                        <p className="text-sm text-gray-600">{maintenance.description}</p>
                        <p className="text-xs text-gray-500">
                          {format(new Date(maintenance.timestamp), 'MMM dd, yyyy')} • {maintenance.performed_by}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">${maintenance.cost}</p>
                        <p className="text-sm text-gray-600">{maintenance.duration_hours}h</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Vehicle Info */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-lg shadow p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Vehicle Information</h2>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <MapPin className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Location</p>
                    <p className="text-sm text-gray-600">{vehicle.location}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Last Maintenance</p>
                    <p className="text-sm text-gray-600">
                      {vehicle.last_maintenance ? format(new Date(vehicle.last_maintenance), 'MMM dd, yyyy') : 'N/A'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Car className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Mileage</p>
                    <p className="text-sm text-gray-600">{vehicle.mileage.toLocaleString()} miles</p>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Health Analysis */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-lg shadow p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Health Analysis</h2>
              {healthData && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Overall Health</span>
                      <span className={`text-sm font-semibold ${getHealthColor(healthData.health_score)}`}>
                        {healthData.health_score}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          healthData.health_score >= 80 ? 'bg-green-500' :
                          healthData.health_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${healthData.health_score}%` }}
                      ></div>
                    </div>
                  </div>

                  {healthData.maintenance_predictions.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-900 mb-2">Upcoming Maintenance</h3>
                      <div className="space-y-2">
                        {healthData.maintenance_predictions.map((prediction, index) => (
                          <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                            <div className="flex items-center space-x-2 mb-1">
                              <Wrench className="w-4 h-4 text-yellow-600" />
                              <span className="text-sm font-medium text-yellow-800 capitalize">
                                {prediction.type.replace('_', ' ')}
                              </span>
                            </div>
                            <p className="text-xs text-yellow-700">{prediction.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {healthData.recommendations.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-900 mb-2">Recommendations</h3>
                      <div className="space-y-2">
                        {healthData.recommendations.map((rec, index) => (
                          <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-blue-800 capitalize">
                                {rec.type.replace('_', ' ')}
                              </span>
                              <span className="text-xs text-blue-600">${rec.estimated_cost}</span>
                            </div>
                            <p className="text-xs text-blue-700">{rec.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-white rounded-lg shadow p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                  Schedule Maintenance
                </button>
                <button className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                  View Reports
                </button>
                <button className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                  Update Status
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VehicleDetail; 