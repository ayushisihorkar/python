import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  Star, 
  CheckCircle, 
  XCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { format, addDays, startOfWeek, endOfWeek, eachDayOfInterval, isSameDay } from 'date-fns';

const BookingCalendar = ({ vehicle, onBookingCreated, onClose }) => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedTime, setSelectedTime] = useState('');
  const [selectedWorkshop, setSelectedWorkshop] = useState(null);
  const [maintenanceType, setMaintenanceType] = useState('');
  const [workshops, setWorkshops] = useState([]);
  const [loading, setLoading] = useState(false);

  const maintenanceTypes = [
    { id: 'oil_change', name: 'Oil Change', duration: 1, cost: 50 },
    { id: 'tire_rotation', name: 'Tire Rotation', duration: 1, cost: 30 },
    { id: 'battery_replacement', name: 'Battery Replacement', duration: 1, cost: 150 },
    { id: 'brake_service', name: 'Brake Service', duration: 3, cost: 200 },
    { id: 'engine_tune_up', name: 'Engine Tune-up', duration: 4, cost: 300 }
  ];

  const timeSlots = [
    '08:00', '09:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00'
  ];

  useEffect(() => {
    // Simulate fetching workshops
    setWorkshops([
      {
        id: 'ws_001',
        name: 'Premium Auto Service',
        location: 'Downtown',
        rating: 4.8,
        cost_multiplier: 1.2,
        services: ['oil_change', 'tire_rotation', 'battery_replacement', 'brake_service'],
        availability: {
          monday: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
          tuesday: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
          wednesday: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
          thursday: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
          friday: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
        }
      },
      {
        id: 'ws_002',
        name: 'Quick Fix Garage',
        location: 'Suburbs',
        rating: 4.2,
        cost_multiplier: 0.9,
        services: ['oil_change', 'tire_rotation', 'battery_replacement'],
        availability: {
          monday: ['08:00', '09:00', '10:00', '13:00', '14:00', '15:00'],
          tuesday: ['08:00', '09:00', '10:00', '13:00', '14:00', '15:00'],
          wednesday: ['08:00', '09:00', '10:00', '13:00', '14:00', '15:00'],
          thursday: ['08:00', '09:00', '10:00', '13:00', '14:00', '15:00'],
          friday: ['08:00', '09:00', '10:00', '13:00', '14:00', '15:00']
        }
      }
    ]);
  }, []);

  const getWeekDays = () => {
    const start = startOfWeek(selectedDate, { weekStartsOn: 1 });
    const end = endOfWeek(selectedDate, { weekStartsOn: 1 });
    return eachDayOfInterval({ start, end });
  };

  const getAvailableTimeSlots = (date) => {
    const dayName = format(date, 'EEEE').toLowerCase();
    const availableSlots = [];
    
    workshops.forEach(workshop => {
      if (workshop.availability[dayName]) {
        availableSlots.push(...workshop.availability[dayName]);
      }
    });
    
    return [...new Set(availableSlots)].sort();
  };

  const getWorkshopsForService = (service) => {
    return workshops.filter(workshop => 
      workshop.services.includes(service)
    );
  };

  const handleBooking = async () => {
    if (!selectedDate || !selectedTime || !selectedWorkshop || !maintenanceType) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const selectedMaintenance = maintenanceTypes.find(m => m.id === maintenanceType);
      const bookingData = {
        vehicle_id: vehicle.id,
        workshop_id: selectedWorkshop.id,
        task_type: maintenanceType,
        scheduled_date: format(selectedDate, 'yyyy-MM-dd'),
        scheduled_time: selectedTime,
        estimated_duration: selectedMaintenance.duration,
        estimated_cost: selectedMaintenance.cost * selectedWorkshop.cost_multiplier,
        urgency: 'medium'
      };

      // In a real app, you would call the API here
      console.log('Creating booking:', bookingData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      onBookingCreated({
        ...bookingData,
        booking_id: `booking_${Date.now()}`,
        workshop_name: selectedWorkshop.name,
        status: 'scheduled'
      });
      
      onClose();
    } catch (error) {
      console.error('Error creating booking:', error);
      alert('Failed to create booking. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const weekDays = getWeekDays();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ y: 50 }}
        animate={{ y: 0 }}
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Schedule Maintenance</h2>
            <p className="text-gray-600">
              {vehicle.make} {vehicle.model} - {vehicle.license_plate}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XCircle className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          {/* Maintenance Type Selection */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Select Maintenance Type</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {maintenanceTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setMaintenanceType(type.id)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    maintenanceType === type.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-left">
                    <p className="font-medium text-gray-900">{type.name}</p>
                    <p className="text-sm text-gray-600">
                      {type.duration}h • ${type.cost}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Workshop Selection */}
          {maintenanceType && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <h3 className="text-lg font-semibold mb-3">Select Workshop</h3>
              <div className="space-y-3">
                {getWorkshopsForService(maintenanceType).map((workshop) => (
                  <button
                    key={workshop.id}
                    onClick={() => setSelectedWorkshop(workshop)}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      selectedWorkshop?.id === workshop.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{workshop.name}</p>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <MapPin className="w-4 h-4" />
                          <span>{workshop.location}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center">
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                          <span className="text-sm font-medium">{workshop.rating}</span>
                        </div>
                        <span className="text-sm text-gray-500">
                          {workshop.cost_multiplier > 1 ? '+' : ''}
                          {Math.round((workshop.cost_multiplier - 1) * 100)}%
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Calendar */}
          {selectedWorkshop && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <h3 className="text-lg font-semibold mb-3">Select Date & Time</h3>
              
              {/* Calendar Navigation */}
              <div className="flex items-center justify-between mb-4">
                <button
                  onClick={() => setSelectedDate(addDays(selectedDate, -7))}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <h4 className="text-lg font-medium">
                  {format(selectedDate, 'MMMM yyyy')}
                </h4>
                <button
                  onClick={() => setSelectedDate(addDays(selectedDate, 7))}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-1 mb-4">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                  <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
                    {day}
                  </div>
                ))}
                {weekDays.map((date) => {
                  const isSelected = isSameDay(date, selectedDate);
                  const availableSlots = getAvailableTimeSlots(date);
                  const hasAvailability = availableSlots.length > 0;
                  
                  return (
                    <button
                      key={date.toISOString()}
                      onClick={() => setSelectedDate(date)}
                      disabled={!hasAvailability}
                      className={`p-2 rounded-lg transition-all ${
                        isSelected
                          ? 'bg-blue-500 text-white'
                          : hasAvailability
                          ? 'hover:bg-gray-100'
                          : 'text-gray-300 cursor-not-allowed'
                      }`}
                    >
                      <div className="text-sm font-medium">
                        {format(date, 'd')}
                      </div>
                      {hasAvailability && (
                        <div className="text-xs opacity-75">
                          {availableSlots.length} slots
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Time Slots */}
              <div className="grid grid-cols-5 gap-2">
                {getAvailableTimeSlots(selectedDate).map((time) => (
                  <button
                    key={time}
                    onClick={() => setSelectedTime(time)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      selectedTime === time
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span className="font-medium">{time}</span>
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Booking Summary */}
          {selectedDate && selectedTime && selectedWorkshop && maintenanceType && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gray-50 rounded-lg p-4 mb-6"
            >
              <h3 className="text-lg font-semibold mb-3">Booking Summary</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Vehicle:</span>
                  <span className="font-medium">{vehicle.make} {vehicle.model}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Service:</span>
                  <span className="font-medium">
                    {maintenanceTypes.find(m => m.id === maintenanceType)?.name}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Workshop:</span>
                  <span className="font-medium">{selectedWorkshop.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Date & Time:</span>
                  <span className="font-medium">
                    {format(selectedDate, 'MMM dd, yyyy')} at {selectedTime}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Estimated Cost:</span>
                  <span className="font-medium">
                    ${(maintenanceTypes.find(m => m.id === maintenanceType)?.cost * selectedWorkshop.cost_multiplier).toFixed(2)}
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleBooking}
              disabled={!selectedDate || !selectedTime || !selectedWorkshop || !maintenanceType || loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Creating Booking...' : 'Confirm Booking'}
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default BookingCalendar; 