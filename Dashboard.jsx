import React, { useState, useEffect } from 'react';
import { 
  Car, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Wrench,
  Plus,
  Search,
  Filter,
  BarChart3,
  Calendar,
  Bell
} from 'lucide-react';
import { motion } from 'framer-motion';
import VehicleCard from '../components/VehicleCard';
import AIAssistantPanel from '../components/AIAssistantPanel';
import Notifications from '../components/Notifications';
import BookingCalendar from '../components/BookingCalendar';

const Dashboard = () => {
  const [vehicles, setVehicles] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showBookingCalendar, setShowBookingCalendar] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  // Sample data - in a real app, this would come from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setVehicles([
          {
            id: 'V001',
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
          },
          {
            id: 'V002',
            make: 'Honda',
            model: 'Civic',
            year: 2021,
            license_plate: 'XYZ789',
            status: 'maintenance',
            location: 'Suburban Lot',
            health_score: 45,
            last_maintenance: '2024-01-10T14:30:00Z',
            mileage: 62000,
            fuel_level: 25.0
          },
          {
            id: 'V003',
            make: 'Ford',
            model: 'Escape',
            year: 2023,
            license_plate: 'DEF456',
            status: 'active',
            location: 'Airport Terminal',
            health_score: 92,
            last_maintenance: '2024-01-20T09:15:00Z',
            mileage: 28000,
            fuel_level: 90.0
          },
          {
            id: 'V004',
            make: 'Chevrolet',
            model: 'Malibu',
            year: 2020,
            license_plate: 'GHI789',
            status: 'out_of_service',
            location: 'Repair Shop',
            health_score: 25,
            last_maintenance: '2024-01-05T16:45:00Z',
            mileage: 78000,
            fuel_level: 10.0
          },
          {
            id: 'V005',
            make: 'Nissan',
            model: 'Altima',
            year: 2022,
            license_plate: 'JKL012',
            status: 'active',
            location: 'City Center',
            health_score: 78,
            last_maintenance: '2024-01-18T11:20:00Z',
            mileage: 38000,
            fuel_level: 60.0
          }
        ]);

        setAlerts([
          {
            id: 'alert_001',
            vehicle_id: 'V002',
            type: 'critical',
            message: 'Low oil pressure detected',
            timestamp: '2024-01-25T10:30:00Z',
            action_required: true,
            read: false
          },
          {
            id: 'alert_002',
            vehicle_id: 'V004',
            type: 'critical',
            message: 'Engine overheating - immediate attention required',
            timestamp: '2024-01-25T10:30:00Z',
            action_required: true,
            read: false
          },
          {
            id: 'alert_003',
            vehicle_id: 'V002',
            type: 'warning',
            message: 'Battery voltage below optimal level',
            timestamp: '2024-01-25T10:30:00Z',
            action_required: true,
            read: true
          }
        ]);

        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredVehicles = vehicles.filter(vehicle => {
    const matchesSearch = vehicle.make.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vehicle.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vehicle.license_plate.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || vehicle.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const fleetStats = {
    total: vehicles.length,
    active: vehicles.filter(v => v.status === 'active').length,
    maintenance: vehicles.filter(v => v.status === 'maintenance').length,
    outOfService: vehicles.filter(v => v.status === 'out_of_service').length,
    avgHealth: vehicles.reduce((sum, v) => sum + (v.health_score || 0), 0) / vehicles.length,
    criticalAlerts: alerts.filter(a => a.type === 'critical').length
  };

  const handleViewDetails = (vehicle) => {
    // Navigate to vehicle detail page
    console.log('View details for vehicle:', vehicle.id);
  };

  const handleScheduleMaintenance = (vehicle) => {
    setSelectedVehicle(vehicle);
    setShowBookingCalendar(true);
  };

  const handleBookingCreated = (booking) => {
    console.log('Booking created:', booking);
    // In a real app, you would update the UI or show a success message
  };

  const handleAIAction = (action) => {
    console.log('AI Action:', action);
    // Handle AI assistant actions
  };

  const handleMarkAlertRead = (alertId) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, read: true } : alert
    ));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading fleet data...</p>
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
              <div className="flex items-center space-x-2">
                <Car className="w-8 h-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">Fleet Dashboard</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Notifications 
                alerts={alerts} 
                onMarkRead={handleMarkAlertRead}
              />
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Car className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Vehicles</p>
                <p className="text-2xl font-bold text-gray-900">{fleetStats.total}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-lg shadow p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-gray-900">{fleetStats.active}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-lg shadow p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Wrench className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">In Maintenance</p>
                <p className="text-2xl font-bold text-gray-900">{fleetStats.maintenance}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Out of Service</p>
                <p className="text-2xl font-bold text-gray-900">{fleetStats.outOfService}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-lg shadow p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Health</p>
                <p className="text-2xl font-bold text-gray-900">{fleetStats.avgHealth.toFixed(1)}%</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-lg shadow p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Bell className="w-6 h-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Critical Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{fleetStats.criticalAlerts}</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search vehicles..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="maintenance">Maintenance</option>
                <option value="out_of_service">Out of Service</option>
                <option value="rented">Rented</option>
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                <BarChart3 className="w-4 h-4" />
                <span>Analytics</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                <Calendar className="w-4 h-4" />
                <span>Schedule</span>
              </button>
            </div>
          </div>
        </div>

        {/* Vehicle Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredVehicles.map((vehicle, index) => (
            <motion.div
              key={vehicle.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <VehicleCard
                vehicle={vehicle}
                onViewDetails={handleViewDetails}
                onScheduleMaintenance={handleScheduleMaintenance}
              />
            </motion.div>
          ))}
        </div>

        {filteredVehicles.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <Car className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No vehicles found</h3>
            <p className="text-gray-600">Try adjusting your search or filter criteria.</p>
          </motion.div>
        )}
      </div>

      {/* AI Assistant */}
      <AIAssistantPanel
        vehicles={vehicles}
        alerts={alerts}
        onAction={handleAIAction}
      />

      {/* Booking Calendar Modal */}
      {showBookingCalendar && selectedVehicle && (
        <BookingCalendar
          vehicle={selectedVehicle}
          onBookingCreated={handleBookingCreated}
          onClose={() => {
            setShowBookingCalendar(false);
            setSelectedVehicle(null);
          }}
        />
      )}
    </div>
  );
};

export default Dashboard; 