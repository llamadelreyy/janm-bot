import React from 'react';
import { RefreshCw, Clock, Database, Settings, BarChart } from 'lucide-react';

const Header = ({ appState, onRefresh }) => {
  const formatLastUpdate = () => {
    return new Date().toLocaleString();
  };

  const getStatusBadge = (condition, successText, warningText) => {
    if (condition) {
      return (
        <span className="badge-success">
          {successText}
        </span>
      );
    }
    return (
      <span className="badge-warning">
        {warningText}
      </span>
    );
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Title and Breadcrumb */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Fraud Detection Dashboard
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Analyze government payment data for fraud patterns
          </p>
        </div>

        {/* Status Summary and Actions */}
        <div className="flex items-center space-x-6">
          {/* Quick Status */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Database className="w-4 h-4 text-gray-500" />
              {getStatusBadge(
                appState.dataUploaded,
                `${appState.dataRows?.toLocaleString()} rows`,
                'No data'
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <Settings className="w-4 h-4 text-gray-500" />
              {getStatusBadge(
                appState.rulesCount > 0,
                `${appState.rulesCount} rules`,
                'No rules'
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <BarChart className="w-4 h-4 text-gray-500" />
              {getStatusBadge(
                appState.analysisCompleted,
                'Analysis done',
                'Not analyzed'
              )}
            </div>
          </div>

          {/* Divider */}
          <div className="h-6 w-px bg-gray-300" />

          {/* Last Update */}
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>Updated: {formatLastUpdate()}</span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            className="btn-ghost btn-sm"
            title="Refresh status"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
          <span>Workflow Progress</span>
          <span>
            {[
              appState.dataUploaded,
              appState.rulesCount > 0,
              appState.analysisCompleted
            ].filter(Boolean).length} of 3 steps completed
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div
            className="bg-gradient-to-r from-primary-500 to-primary-600 h-1.5 rounded-full transition-all duration-500 ease-out"
            style={{
              width: `${
                ([
                  appState.dataUploaded,
                  appState.rulesCount > 0,
                  appState.analysisCompleted
                ].filter(Boolean).length / 3) * 100
              }%`
            }}
          />
        </div>
        
        {/* Step Labels */}
        <div className="flex justify-between mt-2">
          <div className={`text-xs ${appState.dataUploaded ? 'text-primary-600 font-medium' : 'text-gray-400'}`}>
            Upload Data
          </div>
          <div className={`text-xs ${appState.rulesCount > 0 ? 'text-primary-600 font-medium' : 'text-gray-400'}`}>
            Configure Rules
          </div>
          <div className={`text-xs ${appState.analysisCompleted ? 'text-primary-600 font-medium' : 'text-gray-400'}`}>
            Run Analysis
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;