import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Upload, 
  Settings, 
  BarChart3, 
  Download, 
  Shield,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react';

const Sidebar = ({ appState }) => {
  const navItems = [
    {
      path: '/upload',
      icon: Upload,
      label: 'Upload Data',
      description: 'Upload Excel or CSV files'
    },
    {
      path: '/rules',
      icon: Settings,
      label: 'Configure Rules',
      description: 'Set up fraud detection rules'
    },
    {
      path: '/analysis',
      icon: BarChart3,
      label: 'Analysis Results',
      description: 'View fraud analysis results'
    },
    {
      path: '/export',
      icon: Download,
      label: 'Export Data',
      description: 'Download processed data'
    }
  ];

  const getStatusIcon = (condition, successIcon, warningIcon) => {
    if (condition) {
      return <CheckCircle className="w-4 h-4 text-success-600" />;
    }
    return <AlertTriangle className="w-4 h-4 text-warning-600" />;
  };

  const getStatusText = (condition, successText, warningText) => {
    return condition ? successText : warningText;
  };

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo and Title */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Fraud Detection</h1>
            <p className="text-sm text-gray-600">System v1.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors group ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 border border-primary-200'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-medium">{item.label}</div>
                <div className="text-xs text-gray-500 group-hover:text-gray-600">
                  {item.description}
                </div>
              </div>
            </NavLink>
          );
        })}
      </nav>

      {/* Status Panel */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
          <Info className="w-4 h-4 mr-2" />
          Current Status
        </h3>
        
        <div className="space-y-3">
          {/* Data Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStatusIcon(appState.dataUploaded)}
              <span className="text-sm text-gray-700">Data</span>
            </div>
            <div className="text-right">
              <div className="text-xs font-medium text-gray-900">
                {getStatusText(
                  appState.dataUploaded,
                  `${appState.dataRows?.toLocaleString()} rows`,
                  'No data'
                )}
              </div>
              {appState.fileInfo && (
                <div className="text-xs text-gray-500">
                  {appState.fileInfo.name}
                </div>
              )}
            </div>
          </div>

          {/* Rules Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStatusIcon(appState.rulesCount > 0)}
              <span className="text-sm text-gray-700">Rules</span>
            </div>
            <div className="text-xs font-medium text-gray-900">
              {getStatusText(
                appState.rulesCount > 0,
                `${appState.rulesCount} configured`,
                'None configured'
              )}
            </div>
          </div>

          {/* Analysis Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStatusIcon(appState.analysisCompleted)}
              <span className="text-sm text-gray-700">Analysis</span>
            </div>
            <div className="text-xs font-medium text-gray-900">
              {getStatusText(
                appState.analysisCompleted,
                'Completed',
                'Not run'
              )}
            </div>
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Progress</span>
            <span>
              {[
                appState.dataUploaded,
                appState.rulesCount > 0,
                appState.analysisCompleted
              ].filter(Boolean).length}/3
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
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
        </div>
      </div>
    </div>
  );
};

export default Sidebar;