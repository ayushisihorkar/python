import React from 'react'
import { Link } from 'react-router-dom'
import { 
  Battery, 
  Thermometer, 
  Gauge, 
  Droplets, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Calendar,
  MapPin
} from 'lucide-react'

const StatusBadge = ({ status }) => {
  const statusConfig = {
    operational: {
      className: 'status-operational',
      icon: CheckCircle,
      text: 'Operational'
    },
    warning: {
      className: 'status-warning',
      icon: AlertTriangle,
      text: 'Warning'
    },
    critical: {
      className: 'status-critical',
      icon: AlertTriangle,
      text: 'Critical'
    },
    maintenance: {
      className: 'status-maintenance',
      icon: Clock,
      text: 'Maintenance'
    }
  }

  const config = statusConfig[status] || statusConfig.operational
  const Icon = config.icon

  return (
    <span className={`status-pill ${config.className}`}>
      <Icon className="w-3 h-3 mr-1" />
      {config.text}
    </span>
  )
}

const MetricChip = ({ icon: Icon, label, value, unit, status = 'good' }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'critical':
        return 'text-danger-600 bg-danger-50 border-danger-200'
      case 'warning':
        return 'text-warning-600 bg-warning-50 border-warning-200'
      case 'good':
      default:
        return 'text-success-600 bg-success-50 border-success-200'
    }
  }

  return (
    <div className={`inline-flex items-center px-3 py-2 rounded-xl border text-sm font-medium ${getStatusColor(status)}`}>
      <Icon className="w-4 h-4 mr-2" />
      <span className="text-secondary-600 mr-1">{label}:</span>
      <span className="font-semibold">{value}{unit}</span>
    </div>
  )
}

const VehicleCard = ({ vehicle }) => {
  const {
    id,
    vehicle_reg,
    brand,
    model,
    status,
    battery_soh,
    battery_soc,
    motor_efficiency,
    coolant_level,
    battery_temp,
    last_service_date,
    error_codes = []
  } = vehicle

  // Calculate health score based on key metrics
  const calculateHealthScore = () => {
    const metrics = [battery_soh, motor_efficiency, coolant_level].filter(m => m !== null && m !== undefined)
    if (metrics.length === 0) return 85 // Default score
    return Math.round(metrics.reduce((acc, curr) => acc + curr, 0) / metrics.length)
  }

  const healthScore = calculateHealthScore()
  
  // Determine metric statuses
  const getBatteryStatus = () => {
    if (!battery_soh) return 'good'
    if (battery_soh < 70) return 'critical'
    if (battery_soh < 80) return 'warning'
    return 'good'
  }

  const getMotorStatus = () => {
    if (!motor_efficiency) return 'good'
    if (motor_efficiency < 75) return 'critical'
    if (motor_efficiency < 85) return 'warning'
    return 'good'
  }

  const getCoolantStatus = () => {
    if (!coolant_level) return 'good'
    if (coolant_level < 20) return 'critical'
    if (coolant_level < 40) return 'warning'
    return 'good'
  }

  const getTempStatus = () => {
    if (!battery_temp) return 'good'
    if (battery_temp > 45) return 'critical'
    if (battery_temp > 40) return 'warning'
    return 'good'
  }

  // Generate placeholder vehicle image URL
  const getVehicleImageUrl = (brand, model) => {
    // In a real app, this would be actual vehicle images
    const carImages = [
      'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&h=240&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1617788138017-80ad40651399?w=400&h=240&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=400&h=240&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=240&fit=crop&crop=center'
    ]
    
    // Use vehicle ID to consistently select same image
    return carImages[id % carImages.length]
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'No service recorded'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <Link to={`/vehicle/${id}`} className="block">
      <div className="card card-hover group">
        {/* Vehicle Image */}
        <div className="relative h-48 rounded-t-2xl overflow-hidden">
          <img
            src={getVehicleImageUrl(brand, model)}
            alt={`${brand} ${model}`}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
          
          {/* Status Badge Overlay */}
          <div className="absolute top-4 left-4">
            <StatusBadge status={status} />
          </div>
          
          {/* Health Score Badge */}
          <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-xl px-3 py-2">
            <div className="text-xs text-secondary-600 font-medium">Health Score</div>
            <div className={`text-lg font-bold ${
              healthScore >= 90 ? 'text-success-600' :
              healthScore >= 70 ? 'text-warning-600' :
              'text-danger-600'
            }`}>
              {healthScore}%
            </div>
          </div>
          
          {/* Error Indicator */}
          {error_codes.length > 0 && (
            <div className="absolute bottom-4 left-4 bg-danger-100 text-danger-800 rounded-lg px-2 py-1 text-xs font-medium border border-danger-200">
              {error_codes.length} Error{error_codes.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>

        {/* Card Content */}
        <div className="p-6">
          {/* Vehicle Header */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-secondary-900">
                {vehicle_reg}
              </h3>
              <span className="text-sm text-secondary-500 font-mono">
                #{id.toString().padStart(4, '0')}
              </span>
            </div>
            <p className="text-secondary-600 font-medium">
              {brand} {model}
            </p>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {battery_soh && (
              <MetricChip
                icon={Battery}
                label="Battery"
                value={battery_soh}
                unit="%"
                status={getBatteryStatus()}
              />
            )}
            
            {motor_efficiency && (
              <MetricChip
                icon={Gauge}
                label="Motor"
                value={motor_efficiency}
                unit="%"
                status={getMotorStatus()}
              />
            )}
            
            {coolant_level && (
              <MetricChip
                icon={Droplets}
                label="Coolant"
                value={coolant_level}
                unit="%"
                status={getCoolantStatus()}
              />
            )}
            
            {battery_temp && (
              <MetricChip
                icon={Thermometer}
                label="Temp"
                value={battery_temp}
                unit="°C"
                status={getTempStatus()}
              />
            )}
          </div>

          {/* Additional Info */}
          <div className="flex items-center justify-between text-sm text-secondary-500">
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              <span>Last Service: {formatDate(last_service_date)}</span>
            </div>
            
            {battery_soc && (
              <div className="flex items-center">
                <Battery className="w-4 h-4 mr-1" />
                <span>{battery_soc}% Charge</span>
              </div>
            )}
          </div>

          {/* Action Indicators */}
          <div className="mt-4 pt-4 border-t border-secondary-100">
            <div className="flex items-center justify-between">
              <div className="flex space-x-2">
                {status === 'critical' && (
                  <span className="text-xs bg-danger-100 text-danger-700 px-2 py-1 rounded-lg">
                    Immediate Action Required
                  </span>
                )}
                {status === 'warning' && (
                  <span className="text-xs bg-warning-100 text-warning-700 px-2 py-1 rounded-lg">
                    Maintenance Recommended
                  </span>
                )}
              </div>
              
              <span className="text-xs text-secondary-400 group-hover:text-primary-600 transition-colors">
                View Details →
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

export default VehicleCard