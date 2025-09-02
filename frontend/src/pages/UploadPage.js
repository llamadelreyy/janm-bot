import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { 
  Upload, 
  File, 
  CheckCircle, 
  AlertCircle, 
  Database,
  FileText,
  BarChart3,
  Zap
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const UploadPage = ({ onStateUpdate, onShowToast }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedData, setUploadedData] = useState(null);
  const [generatingSample, setGeneratingSample] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setUploadedData(response.data);
        onStateUpdate({
          dataUploaded: true,
          dataRows: response.data.file_info.rows,
          fileInfo: response.data.file_info,
          analysisCompleted: false
        });
        onShowToast('File uploaded successfully!', 'success');
      }
    } catch (error) {
      console.error('Upload error:', error);
      onShowToast(
        error.response?.data?.detail || 'Error uploading file',
        'error'
      );
    } finally {
      setUploading(false);
    }
  }, [onStateUpdate, onShowToast]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    multiple: false,
    maxSize: 200 * 1024 * 1024 // 200MB
  });

  const generateSampleData = async () => {
    setGeneratingSample(true);
    
    try {
      const response = await axios.post('/sample-data');
      
      if (response.data.success) {
        setUploadedData(response.data);
        onStateUpdate({
          dataUploaded: true,
          dataRows: response.data.file_info.rows,
          fileInfo: response.data.file_info,
          analysisCompleted: false
        });
        onShowToast('Sample data generated successfully!', 'success');
      }
    } catch (error) {
      console.error('Sample data error:', error);
      onShowToast(
        error.response?.data?.detail || 'Error generating sample data',
        'error'
      );
    } finally {
      setGeneratingSample(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Data</h1>
        <p className="text-lg text-gray-600">
          Upload your Excel or CSV file to begin fraud detection analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <Upload className="w-5 h-5 mr-2" />
                File Upload
              </h2>
            </div>
            
            <div className="card-content">
              {/* Dropzone */}
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-400 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                }`}
              >
                <input {...getInputProps()} />
                
                {uploading ? (
                  <div className="space-y-4">
                    <LoadingSpinner size="xl" className="mx-auto" />
                    <p className="text-gray-600">Processing file...</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="w-16 h-16 mx-auto bg-primary-100 rounded-full flex items-center justify-center">
                      <Upload className="w-8 h-8 text-primary-600" />
                    </div>
                    
                    <div>
                      <p className="text-lg font-medium text-gray-900">
                        {isDragActive ? 'Drop your file here' : 'Drag & drop your file here'}
                      </p>
                      <p className="text-gray-600 mt-1">
                        or <span className="text-primary-600 font-medium">browse files</span>
                      </p>
                    </div>
                    
                    <div className="text-sm text-gray-500">
                      Supports Excel (.xlsx, .xls) and CSV files up to 200MB
                    </div>
                  </div>
                )}
              </div>

              {/* Sample Data Option */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="text-center">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Need Sample Data?
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Generate sample government payment data with built-in fraud patterns for testing
                  </p>
                  <button
                    onClick={generateSampleData}
                    disabled={generatingSample}
                    className="btn-outline btn-md"
                  >
                    {generatingSample ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 mr-2" />
                        Generate Sample Data
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Guidelines */}
        <div className="space-y-6">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Upload Guidelines</h3>
            </div>
            <div className="card-content space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Supported Formats</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Excel (.xlsx, .xls)</li>
                  <li>• CSV (.csv)</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Limits</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Up to 200,000 rows</li>
                  <li>• Up to 100 columns</li>
                  <li>• Max file size: 200MB</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Requirements</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• First row should contain headers</li>
                  <li>• Data should be clean and consistent</li>
                  <li>• Avoid merged cells in Excel</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">System Capabilities</h3>
            </div>
            <div className="card-content space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Database className="w-4 h-4 text-primary-600" />
                </div>
                <div>
                  <div className="font-medium text-gray-900">Large Dataset Support</div>
                  <div className="text-sm text-gray-600">Process up to 200K rows efficiently</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-4 h-4 text-success-600" />
                </div>
                <div>
                  <div className="font-medium text-gray-900">Smart Detection</div>
                  <div className="text-sm text-gray-600">Automatic column type detection</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-4 h-4 text-warning-600" />
                </div>
                <div>
                  <div className="font-medium text-gray-900">Real-time Analysis</div>
                  <div className="text-sm text-gray-600">Instant data quality insights</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Results */}
      {uploadedData && (
        <div className="card animate-fade-in">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <CheckCircle className="w-5 h-5 mr-2 text-success-600" />
              Upload Successful
            </h2>
          </div>
          
          <div className="card-content">
            {/* File Info */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {uploadedData.file_info.rows.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Rows</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {uploadedData.file_info.columns}
                </div>
                <div className="text-sm text-gray-600">Columns</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {uploadedData.file_info.size}
                </div>
                <div className="text-sm text-gray-600">File Size</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {uploadedData.file_info.extension.toUpperCase()}
                </div>
                <div className="text-sm text-gray-600">Format</div>
              </div>
            </div>

            {/* Columns */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Detected Columns</h3>
              <div className="flex flex-wrap gap-2">
                {uploadedData.columns.map((column, index) => (
                  <span key={index} className="badge-secondary">
                    {column}
                  </span>
                ))}
              </div>
            </div>

            {/* Data Preview */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Data Preview</h3>
              <div className="overflow-x-auto">
                <table className="table">
                  <thead className="table-header">
                    <tr>
                      {uploadedData.columns.map((column, index) => (
                        <th key={index} className="table-header-cell">
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="table-body">
                    {uploadedData.preview.slice(0, 5).map((row, index) => (
                      <tr key={index} className="table-row">
                        {uploadedData.columns.map((column, colIndex) => (
                          <td key={colIndex} className="table-cell">
                            {row[column]?.toString() || '—'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Data Quality */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">Missing Values</h3>
                <div className="space-y-2">
                  {Object.entries(uploadedData.data_quality.missing_values)
                    .filter(([_, count]) => count > 0)
                    .slice(0, 5)
                    .map(([column, count]) => (
                      <div key={column} className="flex justify-between items-center">
                        <span className="text-sm text-gray-700">{column}</span>
                        <span className="badge-warning">{count} missing</span>
                      </div>
                    ))}
                  {Object.values(uploadedData.data_quality.missing_values).every(count => count === 0) && (
                    <div className="text-sm text-success-600 flex items-center">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      No missing values found
                    </div>
                  )}
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">Data Types</h3>
                <div className="space-y-2">
                  {Object.entries(uploadedData.data_quality.data_types)
                    .slice(0, 5)
                    .map(([column, type]) => (
                      <div key={column} className="flex justify-between items-center">
                        <span className="text-sm text-gray-700">{column}</span>
                        <span className="badge-secondary">{type}</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPage;