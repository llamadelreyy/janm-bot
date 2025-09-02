import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Settings, 
  Plus, 
  Trash2, 
  Eye, 
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const RulesPage = ({ appState, onStateUpdate, onShowToast }) => {
  const [rules, setRules] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [comparisonParameters, setComparisonParameters] = useState({});
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRuleForm, setShowRuleForm] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    group_by: '',
    compare: '',
    comparison_parameter: 'same_group_different_values'
  });
  const [previewResults, setPreviewResults] = useState({});
  const [previewingRule, setPreviewingRule] = useState(null);

  useEffect(() => {
    if (appState.dataUploaded) {
      fetchRulesData();
    } else {
      setLoading(false);
    }
  }, [appState.dataUploaded]);

  const fetchRulesData = async () => {
    try {
      const [rulesRes, suggestionsRes, columnsRes] = await Promise.all([
        axios.get('/rules'),
        axios.get('/rule-suggestions'),
        axios.get('/columns')
      ]);

      setRules(rulesRes.data.rules);
      setSuggestions(suggestionsRes.data.suggestions);
      setComparisonParameters(suggestionsRes.data.comparison_parameters);
      setColumns(columnsRes.data.columns);
    } catch (error) {
      console.error('Error fetching rules data:', error);
      onShowToast('Error loading rules data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (e) => {
    e.preventDefault();
    
    if (!newRule.name || !newRule.group_by || !newRule.compare) {
      onShowToast('Please fill in all required fields', 'warning');
      return;
    }

    try {
      const response = await axios.post('/rules', newRule);
      
      if (response.data.success) {
        setRules([...rules, response.data.rule]);
        setNewRule({
          name: '',
          group_by: '',
          compare: '',
          comparison_parameter: 'same_group_different_values'
        });
        setShowRuleForm(false);
        onStateUpdate({ rulesCount: response.data.total_rules });
        onShowToast('Rule created successfully!', 'success');
      }
    } catch (error) {
      console.error('Error creating rule:', error);
      onShowToast(
        error.response?.data?.detail || 'Error creating rule',
        'error'
      );
    }
  };

  const handleDeleteRule = async (index) => {
    try {
      const response = await axios.delete(`/rules/${index}`);
      
      if (response.data.success) {
        setRules(rules.filter((_, i) => i !== index));
        onStateUpdate({ rulesCount: response.data.total_rules });
        onShowToast('Rule deleted successfully!', 'success');
      }
    } catch (error) {
      console.error('Error deleting rule:', error);
      onShowToast('Error deleting rule', 'error');
    }
  };

  const handlePreviewRule = async (index) => {
    setPreviewingRule(index);
    
    try {
      const response = await axios.post(`/rules/${index}/preview`);
      
      if (response.data.success) {
        setPreviewResults({
          ...previewResults,
          [index]: response.data.preview
        });
      }
    } catch (error) {
      console.error('Error previewing rule:', error);
      onShowToast('Error previewing rule', 'error');
    } finally {
      setPreviewingRule(null);
    }
  };

  const handleAddSuggestion = async (suggestion) => {
    const ruleData = {
      name: suggestion.name,
      group_by: suggestion.group_by,
      compare: suggestion.compare,
      comparison_parameter: 'same_group_different_values'
    };

    try {
      const response = await axios.post('/rules', ruleData);
      
      if (response.data.success) {
        setRules([...rules, response.data.rule]);
        onStateUpdate({ rulesCount: response.data.total_rules });
        onShowToast(`Rule "${suggestion.name}" added successfully!`, 'success');
      }
    } catch (error) {
      console.error('Error adding suggested rule:', error);
      onShowToast('Error adding suggested rule', 'error');
    }
  };

  if (!appState.dataUploaded) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <div className="w-16 h-16 mx-auto bg-warning-100 rounded-full flex items-center justify-center mb-4">
          <AlertTriangle className="w-8 h-8 text-warning-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Data Uploaded</h2>
        <p className="text-gray-600 mb-6">
          Please upload data first before configuring fraud detection rules.
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

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <LoadingSpinner size="xl" className="mx-auto mb-4" />
        <p className="text-gray-600">Loading rules configuration...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Configure Rules</h1>
          <p className="text-lg text-gray-600">
            Set up fraud detection rules based on your data columns
          </p>
        </div>
        
        <button
          onClick={() => setShowRuleForm(true)}
          className="btn-primary btn-md"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New Rule
        </button>
      </div>

      {/* Rule Suggestions */}
      {suggestions.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-warning-600" />
              Suggested Rules
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Based on your column names, here are some recommended fraud detection rules
            </p>
          </div>
          
          <div className="card-content">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {suggestions.slice(0, 6).map((suggestion, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-1">
                        {suggestion.name}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        Group by: <span className="font-medium">{suggestion.group_by}</span> → 
                        Compare: <span className="font-medium">{suggestion.compare}</span>
                      </p>
                      <span className={`badge ${
                        suggestion.confidence === 'high' ? 'badge-success' : 'badge-warning'
                      }`}>
                        {suggestion.confidence} confidence
                      </span>
                    </div>
                    <button
                      onClick={() => handleAddSuggestion(suggestion)}
                      className="btn-outline btn-sm ml-3"
                    >
                      Add Rule
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* New Rule Form */}
      {showRuleForm && (
        <div className="card animate-fade-in">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900">Create New Rule</h2>
          </div>
          
          <form onSubmit={handleCreateRule} className="card-content">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <label className="label">Rule Name</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Same IC → Different Bank Account"
                  value={newRule.name}
                  onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <label className="label">Group By Column</label>
                <select
                  className="select"
                  value={newRule.group_by}
                  onChange={(e) => setNewRule({ ...newRule, group_by: e.target.value })}
                  required
                >
                  <option value="">Select column...</option>
                  {columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="label">Compare Column</label>
                <select
                  className="select"
                  value={newRule.compare}
                  onChange={(e) => setNewRule({ ...newRule, compare: e.target.value })}
                  required
                >
                  <option value="">Select column...</option>
                  {columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mb-6">
              <label className="label">Comparison Type</label>
              <select
                className="select"
                value={newRule.comparison_parameter}
                onChange={(e) => setNewRule({ ...newRule, comparison_parameter: e.target.value })}
              >
                {Object.entries(comparisonParameters).map(([key, param]) => (
                  <option key={key} value={key}>
                    {param.name}
                  </option>
                ))}
              </select>
              {comparisonParameters[newRule.comparison_parameter] && (
                <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">
                    <strong>Description:</strong> {comparisonParameters[newRule.comparison_parameter].description
                      .replace('{group_by}', newRule.group_by || '[Group By]')
                      .replace('{compare}', newRule.compare || '[Compare]')}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    <strong>Example:</strong> {comparisonParameters[newRule.comparison_parameter].example}
                  </p>
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowRuleForm(false)}
                className="btn-secondary btn-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary btn-md"
              >
                Create Rule
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Configured Rules */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Configured Rules ({rules.length})
          </h2>
        </div>
        
        <div className="card-content">
          {rules.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Settings className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Rules Configured</h3>
              <p className="text-gray-600 mb-4">
                Create your first fraud detection rule to get started.
              </p>
              <button
                onClick={() => setShowRuleForm(true)}
                className="btn-primary btn-md"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create First Rule
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {rules.map((rule, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {rule.name}
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                        <div>
                          <span className="text-sm text-gray-600">Group By:</span>
                          <div className="font-medium text-gray-900">{rule.group_by}</div>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Compare:</span>
                          <div className="font-medium text-gray-900">{rule.compare}</div>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Type:</span>
                          <div className="font-medium text-gray-900">
                            {comparisonParameters[rule.comparison_parameter]?.name || 'Same Group → Different Values'}
                          </div>
                        </div>
                      </div>

                      {previewResults[index] && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Preview Results:</h4>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                            <div>
                              <span className="text-gray-600">Groups analyzed:</span>
                              <div className="font-medium">{previewResults[index].total_groups}</div>
                            </div>
                            <div>
                              <span className="text-gray-600">Flagged groups:</span>
                              <div className="font-medium">{previewResults[index].flagged_groups}</div>
                            </div>
                            <div>
                              <span className="text-gray-600">Flagged rows:</span>
                              <div className="font-medium">{previewResults[index].flagged_rows}</div>
                            </div>
                            <div>
                              <span className="text-gray-600">Flag rate:</span>
                              <div className="font-medium">{(previewResults[index].flag_rate * 100).toFixed(2)}%</div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handlePreviewRule(index)}
                        disabled={previewingRule === index}
                        className="btn-outline btn-sm"
                      >
                        {previewingRule === index ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDeleteRule(index)}
                        className="btn-ghost btn-sm text-error-600 hover:bg-error-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Help Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Info className="w-5 h-5 mr-2" />
            How Rules Work
          </h3>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Same Group → Different Values</h4>
              <p className="text-sm text-gray-600">
                Flags when the same group (e.g., IC Number) has multiple different values in the compare column (e.g., Bank Account).
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Different Groups → Same Values</h4>
              <p className="text-sm text-gray-600">
                Flags when different groups share the same value in the compare column (e.g., multiple ICs using same bank account).
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Direct Column Mismatch</h4>
              <p className="text-sm text-gray-600">
                Flags when values in two columns don't match as expected (e.g., IC format validation).
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RulesPage;