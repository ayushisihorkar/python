import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  X, 
  Clock,
  MapPin,
  Car,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';

const Notifications = ({ alerts = [], onMarkRead, onClose }) => {
  const [filter, setFilter] = useState('all');
  const [isOpen, setIsOpen] = useState(false);

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !alert.read;
    if (filter === 'critical') return alert.type === 'critical';
    if (filter === 'warning') return alert.type === 'warning';
    return true;
  });

  const getAlertIcon = (type) => {
    switch (type) {
      case 'critical':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'critical':
        return 'border-red-200 bg-red-50';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50';
      case 'info':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getAlertTextColor = (type) => {
    switch (type) {
      case 'critical':
        return 'text-red-800';
      case 'warning':
        return 'text-yellow-800';
      case 'info':
        return 'text-blue-800';
      default:
        return 'text-gray-800';
    }
  };

  const handleMarkRead = (alertId) => {
    if (onMarkRead) {
      onMarkRead(alertId);
    }
  };

  const unreadCount = alerts.filter(alert => !alert.read).length;
  const criticalCount = alerts.filter(alert => alert.type === 'critical').length;

  return (
    <>
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(true)}
        className="relative p-2 text-gray-600 hover:text-gray-800 transition-colors"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </motion.div>
        )}
      </button>

      {/* Notifications Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="absolute top-16 right-4 w-96 bg-white rounded-lg shadow-xl border border-gray-200 max-h-[80vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center space-x-2">
                  <Bell className="w-5 h-5 text-gray-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
                  {unreadCount > 0 && (
                    <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                      {unreadCount} new
                    </span>
                  )}
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Filters */}
              <div className="p-4 border-b bg-gray-50">
                <div className="flex space-x-2">
                  {[
                    { key: 'all', label: 'All', count: alerts.length },
                    { key: 'unread', label: 'Unread', count: unreadCount },
                    { key: 'critical', label: 'Critical', count: criticalCount },
                    { key: 'warning', label: 'Warning', count: alerts.filter(a => a.type === 'warning').length }
                  ].map(({ key, label, count }) => (
                    <button
                      key={key}
                      onClick={() => setFilter(key)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        filter === key
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {label} ({count})
                    </button>
                  ))}
                </div>
              </div>

              {/* Alerts List */}
              <div className="max-h-96 overflow-y-auto">
                {filteredAlerts.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <Bell className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-sm">No notifications to display</p>
                  </div>
                ) : (
                  <div className="p-4 space-y-3">
                    {filteredAlerts.map((alert) => (
                      <motion.div
                        key={alert.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={`p-4 rounded-lg border ${getAlertColor(alert.type)} ${
                          !alert.read ? 'ring-2 ring-blue-200' : ''
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0 mt-1">
                            {getAlertIcon(alert.type)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className={`text-sm font-medium ${getAlertTextColor(alert.type)}`}>
                                {alert.message}
                              </p>
                              <div className="flex items-center space-x-2">
                                {!alert.read && (
                                  <button
                                    onClick={() => handleMarkRead(alert.id)}
                                    className="text-xs text-blue-600 hover:text-blue-700"
                                  >
                                    Mark read
                                  </button>
                                )}
                                <span className="text-xs text-gray-500">
                                  {format(new Date(alert.timestamp), 'MMM dd, HH:mm')}
                                </span>
                              </div>
                            </div>
                            
                            {alert.vehicle_id && (
                              <div className="mt-2 flex items-center space-x-2 text-xs text-gray-600">
                                <Car className="w-3 h-3" />
                                <span>Vehicle: {alert.vehicle_id}</span>
                              </div>
                            )}
                            
                            {alert.action_required && (
                              <div className="mt-2">
                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                  Action Required
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="p-4 border-t bg-gray-50">
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>
                    {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
                  </span>
                  {unreadCount > 0 && (
                    <button
                      onClick={() => {
                        filteredAlerts.forEach(alert => {
                          if (!alert.read) handleMarkRead(alert.id);
                        });
                      }}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Mark all as read
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Notifications; 