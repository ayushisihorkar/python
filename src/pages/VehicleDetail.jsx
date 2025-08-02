import React from 'react'
import { useParams } from 'react-router-dom'

const VehicleDetail = () => {
  const { id } = useParams()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-secondary-900">Vehicle Details</h1>
      <div className="card p-6">
        <p className="text-secondary-600">
          Detailed view for vehicle ID: {id}
        </p>
        <p className="text-sm text-secondary-500 mt-2">
          This page will show comprehensive vehicle telemetry, maintenance history, and AI insights.
        </p>
      </div>
    </div>
  )
}

export default VehicleDetail