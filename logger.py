import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sqlite3
from contextlib import contextmanager

class LoggerAgent:
    """
    AI Agent for logging maintenance history and audit trails
    """
    
    def __init__(self, db_path: str = "maintenance_history.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
        
    def _initialize_database(self):
        """
        Initialize SQLite database with required tables
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Create maintenance history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS maintenance_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vehicle_id TEXT NOT NULL,
                        task_type TEXT NOT NULL,
                        description TEXT,
                        performed_by TEXT,
                        workshop_id TEXT,
                        cost REAL,
                        duration_hours REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'completed',
                        notes TEXT
                    )
                ''')
                
                # Create audit trail table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_trail (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action_type TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        entity_id TEXT NOT NULL,
                        user_id TEXT,
                        details TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create vehicle health logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS health_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vehicle_id TEXT NOT NULL,
                        health_score INTEGER,
                        anomalies TEXT,
                        alerts TEXT,
                        telemetry_data TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create booking history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS booking_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        booking_id TEXT UNIQUE NOT NULL,
                        vehicle_id TEXT NOT NULL,
                        workshop_id TEXT NOT NULL,
                        task_type TEXT NOT NULL,
                        scheduled_date TEXT NOT NULL,
                        scheduled_time TEXT NOT NULL,
                        status TEXT DEFAULT 'scheduled',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
    
    @contextmanager
    def _get_db_connection(self):
        """
        Context manager for database connections
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def log_maintenance_task(self, vehicle_id: str, task_data: Dict) -> Dict:
        """
        Log a completed maintenance task
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO maintenance_history 
                    (vehicle_id, task_type, description, performed_by, workshop_id, cost, duration_hours, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    vehicle_id,
                    task_data.get('task_type'),
                    task_data.get('description'),
                    task_data.get('performed_by'),
                    task_data.get('workshop_id'),
                    task_data.get('cost', 0.0),
                    task_data.get('duration_hours', 0.0),
                    task_data.get('notes')
                ))
                
                conn.commit()
                
                log_entry = {
                    'id': cursor.lastrowid,
                    'vehicle_id': vehicle_id,
                    'task_type': task_data.get('task_type'),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'logged'
                }
                
                self.logger.info(f"Maintenance task logged for vehicle {vehicle_id}")
                return log_entry
                
        except Exception as e:
            self.logger.error(f"Error logging maintenance task: {str(e)}")
            return {'error': str(e)}
    
    def log_health_check(self, vehicle_id: str, health_data: Dict) -> Dict:
        """
        Log vehicle health check results
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO health_logs 
                    (vehicle_id, health_score, anomalies, alerts, telemetry_data)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    vehicle_id,
                    health_data.get('health_score', 0),
                    json.dumps(health_data.get('anomalies', [])),
                    json.dumps(health_data.get('alerts', [])),
                    json.dumps(health_data.get('telemetry_data', {}))
                ))
                
                conn.commit()
                
                log_entry = {
                    'id': cursor.lastrowid,
                    'vehicle_id': vehicle_id,
                    'health_score': health_data.get('health_score'),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'logged'
                }
                
                self.logger.info(f"Health check logged for vehicle {vehicle_id}")
                return log_entry
                
        except Exception as e:
            self.logger.error(f"Error logging health check: {str(e)}")
            return {'error': str(e)}
    
    def log_booking(self, booking_data: Dict) -> Dict:
        """
        Log a maintenance booking
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO booking_history 
                    (booking_id, vehicle_id, workshop_id, task_type, scheduled_date, scheduled_time, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    booking_data.get('booking_id'),
                    booking_data.get('vehicle_id'),
                    booking_data.get('workshop_id'),
                    booking_data.get('task_type'),
                    booking_data.get('scheduled_date'),
                    booking_data.get('scheduled_time'),
                    booking_data.get('status', 'scheduled')
                ))
                
                conn.commit()
                
                log_entry = {
                    'id': cursor.lastrowid,
                    'booking_id': booking_data.get('booking_id'),
                    'vehicle_id': booking_data.get('vehicle_id'),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'logged'
                }
                
                self.logger.info(f"Booking logged: {booking_data.get('booking_id')}")
                return log_entry
                
        except Exception as e:
            self.logger.error(f"Error logging booking: {str(e)}")
            return {'error': str(e)}
    
    def log_audit_event(self, action_type: str, entity_type: str, entity_id: str, 
                       user_id: Optional[str] = None, details: Optional[Dict] = None) -> Dict:
        """
        Log an audit trail event
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO audit_trail 
                    (action_type, entity_type, entity_id, user_id, details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    action_type,
                    entity_type,
                    entity_id,
                    user_id,
                    json.dumps(details) if details else None
                ))
                
                conn.commit()
                
                audit_entry = {
                    'id': cursor.lastrowid,
                    'action_type': action_type,
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'logged'
                }
                
                self.logger.info(f"Audit event logged: {action_type} on {entity_type} {entity_id}")
                return audit_entry
                
        except Exception as e:
            self.logger.error(f"Error logging audit event: {str(e)}")
            return {'error': str(e)}
    
    def get_maintenance_history(self, vehicle_id: str, limit: int = 50) -> List[Dict]:
        """
        Get maintenance history for a vehicle
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM maintenance_history 
                    WHERE vehicle_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (vehicle_id, limit))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                history = []
                for row in rows:
                    history.append(dict(zip(columns, row)))
                
                return history
                
        except Exception as e:
            self.logger.error(f"Error retrieving maintenance history: {str(e)}")
            return []
    
    def get_health_logs(self, vehicle_id: str, limit: int = 50) -> List[Dict]:
        """
        Get health logs for a vehicle
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM health_logs 
                    WHERE vehicle_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (vehicle_id, limit))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                logs = []
                for row in rows:
                    log_entry = dict(zip(columns, row))
                    # Parse JSON fields
                    if log_entry.get('anomalies'):
                        log_entry['anomalies'] = json.loads(log_entry['anomalies'])
                    if log_entry.get('alerts'):
                        log_entry['alerts'] = json.loads(log_entry['alerts'])
                    if log_entry.get('telemetry_data'):
                        log_entry['telemetry_data'] = json.loads(log_entry['telemetry_data'])
                    logs.append(log_entry)
                
                return logs
                
        except Exception as e:
            self.logger.error(f"Error retrieving health logs: {str(e)}")
            return []
    
    def get_booking_history(self, vehicle_id: str, limit: int = 50) -> List[Dict]:
        """
        Get booking history for a vehicle
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM booking_history 
                    WHERE vehicle_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (vehicle_id, limit))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                bookings = []
                for row in rows:
                    bookings.append(dict(zip(columns, row)))
                
                return bookings
                
        except Exception as e:
            self.logger.error(f"Error retrieving booking history: {str(e)}")
            return []
    
    def get_audit_trail(self, entity_type: Optional[str] = None, entity_id: Optional[str] = None, 
                        limit: int = 100) -> List[Dict]:
        """
        Get audit trail entries
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM audit_trail WHERE 1=1"
                params = []
                
                if entity_type:
                    query += " AND entity_type = ?"
                    params.append(entity_type)
                
                if entity_id:
                    query += " AND entity_id = ?"
                    params.append(entity_id)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                audit_entries = []
                for row in rows:
                    audit_entry = dict(zip(columns, row))
                    if audit_entry.get('details'):
                        audit_entry['details'] = json.loads(audit_entry['details'])
                    audit_entries.append(audit_entry)
                
                return audit_entries
                
        except Exception as e:
            self.logger.error(f"Error retrieving audit trail: {str(e)}")
            return []
    
    def export_maintenance_report(self, vehicle_id: str, start_date: str, end_date: str) -> Dict:
        """
        Export maintenance report for a vehicle
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM maintenance_history 
                    WHERE vehicle_id = ? AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                ''', (vehicle_id, start_date, end_date))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                maintenance_entries = []
                total_cost = 0.0
                total_duration = 0.0
                
                for row in rows:
                    entry = dict(zip(columns, row))
                    maintenance_entries.append(entry)
                    total_cost += entry.get('cost', 0.0)
                    total_duration += entry.get('duration_hours', 0.0)
                
                report = {
                    'vehicle_id': vehicle_id,
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_entries': len(maintenance_entries),
                    'total_cost': total_cost,
                    'total_duration': total_duration,
                    'maintenance_entries': maintenance_entries,
                    'generated_at': datetime.now().isoformat()
                }
                
                return report
                
        except Exception as e:
            self.logger.error(f"Error generating maintenance report: {str(e)}")
            return {'error': str(e)} 