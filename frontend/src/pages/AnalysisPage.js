import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart3, 
  Play, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp,
  Users,
  Flag,
  Database
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import LoadingSpinner from '../components/LoadingSpinner';

const AnalysisPage = ({ appState, onStateUpdate, onShowToast }) => {
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    if (appState.analysisCompleted) {
      fetchAnalysisResults();
    }
  }, [appState.analysisCompleted]);

  const fetchAnalysisResults = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/analysis/results');
      setAnalysisResults(response.data);
    } catch (error) {
      console.error('Error fetching analysis results:', error);
      onShowToast('Error loading analysis results', 'error');
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    setAnalyzing(true);
    try {
      const response = await axios.post('/analyze');
      
      if (response.data.success) {
        setAnalysisResults(response.data);
        onStateUpdate({ analysisCompleted: true });
        onShowToast('Analysis completed successfully!', 'success');
      }
    } catch (error) {
      console.error('Error running analysis:', error);
      onShowToast(
        error.response?.data?.detail || 'Error running analysis',
        'error'
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const formatPercentage = (value) => `${(value * 100).toFixed(2)}%`;

  const getChartData = () => {
    if (!analysisResults?.rule_results) return [];
    
    return analysisResults.rule_results.map(result => ({
      name: result.rule_name.length > 20 ? 
        result.rule_name.substring(0, 20) + '...' : 
        result.rule_name,
      flagged: result.flagged_count,
      rate: result.flag_rate * 100
    }));
  };

  const getPieData = () => {
    if (!analysisResults) return [];
    
    const clean = analysisResults.total_rows - analysisResults.total_flagged;
    return [
      { name: 'Clean Records', value: clean, color: '#22c55e' },
      { name: 'Flagged Records', value: analysisResults.total_flagged, color: '#ef4444' }
    ];
  };

  const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#f97316'];

  if (!appState.dataUploaded) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <div className="w-16 h-16 mx-auto bg-warning-100 rounded-full flex items-center justify-center mb-4">
          <AlertTriangle className="w-8 h-8 text-warning-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Data Uploaded</h2>
        <p className="text-gray-600 mb-6">
          Please upload data first before running fraud analysis.
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

  if (appState.rulesCount === 0) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <div className="w-16 h-16 mx-auto bg-warning-100 rounded-full flex items-center justify-center mb-4">
          <AlertTriangle className="w-8 h-8 text-warning-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Rules Configured</h2>
        <p className="text-gray-600 mb-6">
          Please configure at least one fraud detection rule before running analysis.
        </p>
        <button
          onClick={() => window.location.href = '/rules'}
          className="btn-primary btn-md"
        >
          Configure Rules
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analysis Results</h1>
          <p className="text-lg text-gray-600">
            Fraud detection analysis results and insights
          </p>
        </div>
        
        <button
          onClick={runAnalysis}
          disabled={analyzing}
          className="btn-primary btn-lg"
        >
          {analyzing ? (
            <>
              <LoadingSpinner size="sm" className="mr-2" />
              Analyzing...
            </>
          ) : (
            <>
              <Play className="w-5 h-5 mr-2" />
              Run Analysis
            </>
          )}
        </button>
      </div>

      {loading && (
        <div className="text-center py-12">
          <LoadingSpinner size="xl" className="mx-auto mb-4" />
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      )}

      {analysisResults && (
        <div className="space-y-6 animate-fade-in">
          {/* Summary Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card">
              <div className="card-content">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Database className="w-6 h-6 text-primary-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Rows</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analysisResults.total_rows?.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-content">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-error-100 rounded-lg flex items-center justify-center">
                    <Flag className="w-6 h-6 text-error-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Flagged Rows</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analysisResults.total_flagged?.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-content">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-warning-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Flag Rate</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatPercentage(analysisResults.overall_flag_rate)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-content">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center">
                    <Users className="w-6 h-6 text-success-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Rules Applied</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analysisResults.rules_count}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Flag Rate by Rule */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Flag Rate by Rule (%)</h3>
              </div>
              <div className="card-content">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={getChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      fontSize={12}
                    />
                    <YAxis />
                    <Tooltip 
                      formatter={(value) => [`${value.toFixed(2)}%`, 'Flag Rate']}
                    />
                    <Bar dataKey="rate" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Overall Data Distribution */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Data Distribution</h3>
              </div>
              <div className="card-content">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={getPieData()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {getPieData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Flagged Records by Rule */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Flagged Records by Rule</h3>
            </div>
            <div className="card-content">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={getChartData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip 
                    formatter={(value) => [value.toLocaleString(), 'Flagged Records']}
                  />
                  <Bar dataKey="flagged" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Rule Results Details */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Rule Results Details</h3>
            </div>
            <div className="card-content">
              <div className="space-y-6">
                {analysisResults.rule_results.map((result, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <h4 className="text-lg font-medium text-gray-900">
                        {result.rule_name}
                      </h4>
                      <span className={`badge ${
                        result.success ? 'badge-success' : 'badge-error'
                      }`}>
                        {result.success ? 'Success' : 'Failed'}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-xl font-bold text-gray-900">
                          {result.flagged_count?.toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-600">Flagged Rows</div>
                      </div>
                      
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-xl font-bold text-gray-900">
                          {formatPercentage(result.flag_rate)}
                        </div>
                        <div className="text-sm text-gray-600">Flag Rate</div>
                      </div>
                      
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-xl font-bold text-gray-900">
                          {result.flagged_groups || 0}
                        </div>
                        <div className="text-sm text-gray-600">Flagged Groups</div>
                      </div>
                    </div>

                    {/* Sample Flagged Data */}
                    {result.flagged_data_preview && result.flagged_data_preview.length > 0 && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-3">Sample Flagged Records</h5>
                        <div className="overflow-x-auto">
                          <table className="table">
                            <thead className="table-header">
                              <tr>
                                {Object.keys(result.flagged_data_preview[0]).map((key) => (
                                  <th key={key} className="table-header-cell">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="table-body">
                              {result.flagged_data_preview.slice(0, 5).map((row, rowIndex) => (
                                <tr key={rowIndex} className="table-row">
                                  {Object.values(row).map((value, cellIndex) => (
                                    <td key={cellIndex} className="table-cell">
                                      {value?.toString() || '—'}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        {result.flagged_count > 5 && (
                          <p className="text-sm text-gray-600 mt-2">
                            ... and {result.flagged_count - 5} more flagged records
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {!analysisResults && !loading && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto bg-primary-100 rounded-full flex items-center justify-center mb-4">
            <BarChart3 className="w-8 h-8 text-primary-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Analyze</h3>
          <p className="text-gray-600 mb-6">
            Click "Run Analysis" to start fraud detection on your data with the configured rules.
          </p>
          <button
            onClick={runAnalysis}
            disabled={analyzing}
            className="btn-primary btn-lg"
          >
            {analyzing ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="w-5 h-5 mr-2" />
                Run Analysis
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage;