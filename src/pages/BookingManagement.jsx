import React from 'react'
import { Calendar, Clock, MapPin } from 'lucide-react'

const BookingManagement = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Booking Management</h1>
          <p className="text-secondary-600 mt-1">
            Schedule and manage maintenance appointments
          </p>
        </div>
        <button className="btn btn-primary btn-md">
          <Calendar className="w-4 h-4 mr-2" />
          New Booking
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar View */}
        <div className="lg:col-span-2 card p-6">
          <h2 className="text-lg font-semibold text-secondary-900 mb-4">Calendar View</h2>
          <div className="bg-secondary-50 rounded-xl p-8 text-center">
            <Calendar className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
            <p className="text-secondary-600">Calendar component will be implemented here</p>
            <p className="text-sm text-secondary-500 mt-2">
              Interactive booking calendar with workshop availability
            </p>
          </div>
        </div>

        {/* Upcoming Bookings */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-secondary-900 mb-4">Upcoming Bookings</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((booking) => (
              <div key={booking} className="border border-secondary-200 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-secondary-900">EV00{booking}</span>
                  <span className="status-pill status-operational">Confirmed</span>
                </div>
                <div className="text-sm text-secondary-600 space-y-1">
                  <div className="flex items-center">
                    <Clock className="w-3 h-3 mr-2" />
                    Jan {25 + booking}, 2024 - 10:00 AM
                  </div>
                  <div className="flex items-center">
                    <MapPin className="w-3 h-3 mr-2" />
                    AutoTech Center
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default BookingManagement