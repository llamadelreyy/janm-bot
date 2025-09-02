import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';

// Components
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import UploadPage from './pages/UploadPage';
import RulesPage from './pages/RulesPage';
import AnalysisPage from './pages/AnalysisPage';
import ExportPage from './pages/ExportPage';
import LoadingSpinner from './components/LoadingSpinner';
import Toast from './components/Toast';

// API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL;

function App() {
  const [appState, setAppState] = useState({
    dataUploaded: false,
    dataRows: 0,
    rulesCount: 0,
    analysisCompleted: false,
    fileInfo: null
  });
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  // Fetch app status on mount
  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get('/status');
      setAppState(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
      showToast('Error connecting to server', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message, type = 'info', duration = 5000) => {
    setToast({ message, type, id: Date.now() });
    setTimeout(() => setToast(null), duration);
  };

  const updateAppState = (updates) => {
    setAppState(prev => ({ ...prev, ...updates }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading Fraud Detection System...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex">
        {/* Sidebar */}
        <Sidebar appState={appState} />
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <Header appState={appState} onRefresh={fetchStatus} />
          
          {/* Page Content */}
          <main className="flex-1 p-6 overflow-auto">
            <Routes>
              <Route 
                path="/" 
                element={<Navigate to="/upload" replace />} 
              />
              <Route 
                path="/upload" 
                element={
                  <UploadPage 
                    onStateUpdate={updateAppState}
                    onShowToast={showToast}
                  />
                } 
              />
              <Route 
                path="/rules" 
                element={
                  <RulesPage 
                    appState={appState}
                    onStateUpdate={updateAppState}
                    onShowToast={showToast}
                  />
                } 
              />
              <Route 
                path="/analysis" 
                element={
                  <AnalysisPage 
                    appState={appState}
                    onStateUpdate={updateAppState}
                    onShowToast={showToast}
                  />
                } 
              />
              <Route 
                path="/export" 
                element={
                  <ExportPage 
                    appState={appState}
                    onShowToast={showToast}
                  />
                } 
              />
            </Routes>
          </main>
        </div>
        
        {/* Toast Notifications */}
        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
          />
        )}
      </div>
    </Router>
  );
}

export default App;