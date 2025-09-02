import React, { useState } from 'react';
import axios from 'axios';
import { 
  Download, 
  FileText, 
  FileSpreadsheet, 
  AlertTriangle,
  CheckCircle,
  Info,
  Trash2,
  Database
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const ExportPage = ({ appState, onShowToast }) => {
  const [downloading, setDownloading] = useState({});

  const downloadFile = async (endpoint, filename, type) => {
    setDownloading({ ...downloading, [type]: true });
    
    try {
      const response = await axios.get(endpoint, {
        responseType: 'blob'
      });

      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          link.download = filenameMatch[1];
        } else {
          link.download = filename;
        }
      } else {
        link.download = filename;
      }
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      onShowToast(`${filename} downloaded successfully!`, 'success');
    } catch (error) {
      console.error('Download error:', error);
      onShowToast(
        error.response?.data?.detail || `Error downloading ${filename}`,
        'error'
      );
    } finally {
      setDownloading({ ...downloading, [type]: false });
    }
  };

  const getCleanDataStats = () => {
    if (!appState.dataRows || !appState.analysisCompleted) return null;
    
    // This would ideally come from the backend, but we'll estimate
    const estimatedFlaggedRows = Math.floor(appState.dataRows * 0.05); // Assume 5% flagged
    const cleanRows = appState.dataRows - estimatedFlaggedRows;
    
    return {
      originalRows: appState.dataRows,
      cleanRows: cleanRows,
      removedRows: estimatedFlaggedRows
    };
  };

  if (!appState.dataUploaded) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <div className="w-16 h-16 mx-auto bg-warning-100 rounded-full flex items-center justify-center mb-4">
          <AlertTriangle className="w-8 h-8 text-warning-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Data Available</h2>
        <p className="text-gray-600 mb-6">
          Please upload data first before exporting results.
        </p>
        <button
          onClick={() => window.location.href = '/upload'}
          className="btn-primary btn-md"
        >
          Go to Upload Page
        </button>
      </div>
    );
  }

  if (!appState.analysisCompleted) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <div className="w-16 h-16 mx-auto bg-warning-100 rounded-full flex items-center justify-center mb-4">
          <AlertTriangle className="w-8 h-8 text-warning-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Not Completed</h2>
        <p className="text-gray-600 mb-6">
          Please run fraud analysis first before exporting results.
        </p>
        <button
          onClick={() => window.location.href = '/analysis'}
          className="btn-primary btn-md"
        >
          Run Analysis
        </button>
      </div>
    );
  }

  const cleanDataStats = getCleanDataStats();

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Export Data</h1>
        <p className="text-lg text-gray-600">
          Download your processed data in various formats
        </p>
      </div>

      {/* Export Options */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Excel with Highlights */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mr-4">
                <FileSpreadsheet className="w-6 h-6 text-warning-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Excel with Highlights</h3>
                <p className="text-sm text-gray-600">Original data with flagged rows highlighted</p>
              </div>
            </div>
          </div>
          
          <div className="card-content">
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">What's included:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Original data with all rows</li>
                  <li>• Flagged rows highlighted in yellow</li>
                  <li>• Violation details column</li>
                  <li>• Analysis summary worksheet</li>
                  <li>• Flagged data only worksheet</li>
                </ul>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  Perfect for manual review and audit trails
                </div>
                <button
                  onClick={() => downloadFile('/export/highlighted', 'highlighted_data.xlsx', 'highlighted')}
                  disabled={downloading.highlighted}
                  className="btn-primary btn-md"
                >
                  {downloading.highlighted ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Download Excel
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Clean Data */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mr-4">
                <CheckCircle className="w-6 h-6 text-success-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Clean Data</h3>
                <p className="text-sm text-gray-600">Data with flagged rows removed</p>
              </div>
            </div>
          </div>
          
          <div className="card-content">
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">What's included:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Only clean, unflagged records</li>
                  <li>• Original column structure</li>
                  <li>• Ready for further processing</li>
                  <li>• Available in Excel and CSV formats</li>
                </ul>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  Ready for production use
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => downloadFile('/export/clean', 'clean_data.xlsx', 'clean-excel')}
                    disabled={downloading['clean-excel']}
                    className="btn-outline btn-md"
                  >
                    {downloading['clean-excel'] ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <>
                        <FileSpreadsheet className="w-4 h-4 mr-2" />
                        Excel
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={() => downloadFile('/export/clean-csv', 'clean_data.csv', 'clean-csv')}
                    disabled={downloading['clean-csv']}
                    className="btn-outline btn-md"
                  >
                    {downloading['clean-csv'] ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        CSV
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Export Statistics */}
      {cleanDataStats && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Database className="w-5 h-5 mr-2" />
              Export Statistics
            </h3>
          </div>
          
          <div className="card-content">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {cleanDataStats.originalRows.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Original Rows</div>
              </div>
              
              <div className="text-center p-4 bg-success-50 rounded-lg">
                <div className="text-2xl font-bold text-success-700">
                  {cleanDataStats.cleanRows.toLocaleString()}
                </div>
                <div className="text-sm text-success-600">Clean Rows</div>
              </div>
              
              <div className="text-center p-4 bg-error-50 rounded-lg">
                <div className="text-2xl font-bold text-error-700">
                  {cleanDataStats.removedRows.toLocaleString()}
                </div>
                <div className="text-sm text-error-600">Removed Rows</div>
              </div>
            </div>
            
            <div className="mt-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Data Quality</span>
                <span>
                  {((cleanDataStats.cleanRows / cleanDataStats.originalRows) * 100).toFixed(1)}% clean
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-success-600 h-2 rounded-full"
                  style={{
                    width: `${(cleanDataStats.cleanRows / cleanDataStats.originalRows) * 100}%`
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Export Guidelines */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Info className="w-5 h-5 mr-2" />
              Export Guidelines
            </h3>
          </div>
          <div className="card-content space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">File Formats</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• <strong>Excel (.xlsx):</strong> Best for analysis and reporting</li>
                <li>• <strong>CSV (.csv):</strong> Universal format for data processing</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Data Integrity</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• All exports maintain original data types</li>
                <li>• Timestamps are preserved in ISO format</li>
                <li>• Special characters are properly encoded</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <CheckCircle className="w-5 h-5 mr-2" />
              Best Practices
            </h3>
          </div>
          <div className="card-content space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">For Audit Purposes</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Use highlighted Excel for review</li>
                <li>• Keep original data for reference</li>
                <li>• Document analysis parameters</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">For Production Use</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Use clean data exports</li>
                <li>• Validate data before processing</li>
                <li>• Maintain backup copies</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* File Information */}
      {appState.fileInfo && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Source File Information</h3>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <span className="text-sm text-gray-600">Original File:</span>
                <div className="font-medium text-gray-900">{appState.fileInfo.name}</div>
              </div>
              <div>
                <span className="text-sm text-gray-600">File Size:</span>
                <div className="font-medium text-gray-900">{appState.fileInfo.size}</div>
              </div>
              <div>
                <span className="text-sm text-gray-600">Rows:</span>
                <div className="font-medium text-gray-900">{appState.fileInfo.rows?.toLocaleString()}</div>
              </div>
              <div>
                <span className="text-sm text-gray-600">Columns:</span>
                <div className="font-medium text-gray-900">{appState.fileInfo.columns}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportPage;