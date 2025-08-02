import React, { useState, useEffect } from 'react'
import VehicleCard from '../components/VehicleCard'
import { 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Filter,
  Plus,
  Zap
} from 'lucide-react'

const Dashboard = () => {
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  // Sample vehicle data (in real app, this would come from API)
  const sampleVehicles = [
    {
      id: 1,
      vehicle_reg: 'EV001',
      brand: 'Tesla',
      model: 'Model 3',
      status: 'operational',
      battery_soh: 95,
      battery_soc: 87,
      motor_efficiency: 92,
      coolant_level: 85,
      battery_temp: 32,
      last_service_date: '2024-01-15',
      error_codes: []
    },
    {
      id: 2,
      vehicle_reg: 'EV002',
      brand: 'BMW',
      model: 'i4',
      status: 'warning',
      battery_soh: 78,
      battery_soc: 45,
      motor_efficiency: 88,
      coolant_level: 65,
      battery_temp: 42,
      last_service_date: '2023-12-08',
      error_codes: ['TEMP_002']
    },
    {
      id: 3,
      vehicle_reg: 'EV003',
      brand: 'Audi',
      model: 'e-tron',
      status: 'critical',
      battery_soh: 68,
      battery_soc: 23,
      motor_efficiency: 74,
      coolant_level: 18,
      battery_temp: 47,
      last_service_date: '2023-11-22',
      error_codes: ['BATT_001', 'COOL_003']
    },
    {
      id: 4,
      vehicle_reg: 'EV004',
      brand: 'Volkswagen',
      model: 'ID.4',
      status: 'operational',
      battery_soh: 91,
      battery_soc: 78,
      motor_efficiency: 89,
      coolant_level: 92,
      battery_temp: 35,
      last_service_date: '2024-01-20',
      error_codes: []
    },
    {
      id: 5,
      vehicle_reg: 'EV005',
      brand: 'Mercedes',
      model: 'EQS',
      status: 'maintenance',
      battery_soh: 85,
      battery_soc: 0,
      motor_efficiency: 90,
      coolant_level: 88,
      battery_temp: 28,
      last_service_date: '2024-01-25',
      error_codes: []
    },
    {
      id: 6,
      vehicle_reg: 'EV006',
      brand: 'Nissan',
      model: 'Ariya',
      status: 'operational',
      battery_soh: 88,
      battery_soc: 91,
      motor_efficiency: 87,
      coolant_level: 78,
      battery_temp: 31,
      last_service_date: '2024-01-10',
      error_codes: []
    }
  ]

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setVehicles(sampleVehicles)
      setLoading(false)
    }, 1000)
  }, [])

  const getFilteredVehicles = () => {
    if (filter === 'all') return vehicles
    return vehicles.filter(vehicle => vehicle.status === filter)
  }

  const getFleetStats = () => {
    const total = vehicles.length
    const operational = vehicles.filter(v => v.status === 'operational').length
    const warning = vehicles.filter(v => v.status === 'warning').length
    const critical = vehicles.filter(v => v.status === 'critical').length
    const maintenance = vehicles.filter(v => v.status === 'maintenance').length

    const avgBatteryHealth = vehicles
      .filter(v => v.battery_soh)
      .reduce((acc, v) => acc + v.battery_soh, 0) / vehicles.filter(v => v.battery_soh).length

    return {
      total,
      operational,
      warning,
      critical,
      maintenance,
      avgBatteryHealth: Math.round(avgBatteryHealth || 0)
    }
  }

  const stats = getFleetStats()
  const filteredVehicles = getFilteredVehicles()

  const StatCard = ({ title, value, icon: Icon, color, change, description }) => (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-secondary-600">{title}</p>
          <p className="text-2xl font-bold text-secondary-900 mt-2">{value}</p>
          {change && (
            <p className={`text-sm mt-1 ${change >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
              {change >= 0 ? '+' : ''}{change}% from last week
            </p>
          )}
          {description && (
            <p className="text-xs text-secondary-500 mt-1">{description}</p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )

  const FilterButton = ({ status, label, count }) => (
    <button
      onClick={() => setFilter(status)}
      className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
        filter === status
          ? 'bg-primary-600 text-white'
          : 'bg-white text-secondary-600 hover:bg-secondary-100 border border-secondary-200'
      }`}
    >
      {label} {count > 0 && `(${count})`}
    </button>
  )

  if (loading) {
    return (
      <div className="space-y-8">
        {/* Loading skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-4 bg-secondary-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-secondary-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-secondary-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-48 bg-secondary-200 rounded-t-2xl"></div>
              <div className="p-6 space-y-3">
                <div className="h-4 bg-secondary-200 rounded w-3/4"></div>
                <div className="h-3 bg-secondary-200 rounded w-1/2"></div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="h-8 bg-secondary-200 rounded"></div>
                  <div className="h-8 bg-secondary-200 rounded"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Fleet Dashboard</h1>
          <p className="text-secondary-600 mt-1">
            Monitor and manage your electric vehicle fleet with AI-powered insights
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="btn btn-secondary btn-md">
            <Filter className="w-4 h-4 mr-2" />
            Export Report
          </button>
          <button className="btn btn-primary btn-md">
            <Plus className="w-4 h-4 mr-2" />
            Add Vehicle
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Vehicles"
          value={stats.total}
          icon={Zap}
          color="bg-primary-100 text-primary-600"
          change={8}
          description="Active in fleet"
        />
        <StatCard
          title="Operational"
          value={stats.operational}
          icon={CheckCircle}
          color="bg-success-100 text-success-600"
          change={12}
          description="Ready for service"
        />
        <StatCard
          title="Need Attention"
          value={stats.warning + stats.critical}
          icon={AlertTriangle}
          color="bg-warning-100 text-warning-600"
          change={-5}
          description="Maintenance required"
        />
        <StatCard
          title="Avg Battery Health"
          value={`${stats.avgBatteryHealth}%`}
          icon={TrendingUp}
          color="bg-secondary-100 text-secondary-600"
          change={2}
          description="Fleet average SOH"
        />
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-3">
          <FilterButton status="all" label="All Vehicles" count={stats.total} />
          <FilterButton status="operational" label="Operational" count={stats.operational} />
          <FilterButton status="warning" label="Warning" count={stats.warning} />
          <FilterButton status="critical" label="Critical" count={stats.critical} />
          <FilterButton status="maintenance" label="Maintenance" count={stats.maintenance} />
        </div>
        
        <div className="text-sm text-secondary-500">
          Showing {filteredVehicles.length} of {stats.total} vehicles
        </div>
      </div>

      {/* Vehicle Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredVehicles.map((vehicle) => (
          <VehicleCard key={vehicle.id} vehicle={vehicle} />
        ))}
      </div>

      {filteredVehicles.length === 0 && (
        <div className="text-center py-12">
          <AlertTriangle className="mx-auto h-12 w-12 text-secondary-400" />
          <h3 className="mt-2 text-sm font-medium text-secondary-900">No vehicles found</h3>
          <p className="mt-1 text-sm text-secondary-500">
            Try adjusting your filter criteria.
          </p>
        </div>
      )}
    </div>
  )
}

export default Dashboard