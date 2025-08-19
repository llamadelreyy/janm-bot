import pandas as pd
from typing import Dict, List, Any, Optional
import json
import streamlit as st

class RuleEngine:
    """Manages fraud detection rules and their configurations."""
    
    def __init__(self):
        self.comparison_parameters = {
            'same_group_different_values': {
                'name': 'Same Group → Different Values',
                'description': 'Flag when same {group_by} has multiple different {compare} values',
                'logic': 'group_by_multiple_values',
                'example': 'Same Name → Different Bank Accounts'
            },
            'different_group_same_values': {
                'name': 'Different Group → Same Values',
                'description': 'Flag when different {group_by} share the same {compare} value',
                'logic': 'different_groups_same_value',
                'example': 'Different Names → Same Bank Account'
            },
            'direct_column_mismatch': {
                'name': 'Direct Column Mismatch',
                'description': 'Flag when {group_by} is not equal to {compare} in the same row',
                'logic': 'direct_column_comparison',
                'example': 'IC Number ≠ Expected IC Format'
            }
        }
        
        self.rule_templates = {
            'same_group_different_value': {
                'name': 'Same {group_by} → Different {compare}',
                'description': 'Flag records where the same {group_by} has different {compare} values',
                'logic': 'group_by_unique_compare'
            }
        }
    
    def create_rule(self,
                   name: str,
                   group_by_column: str,
                   compare_column: str,
                   comparison_parameter: str = 'same_group_different_values',
                   rule_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new fraud detection rule.
        
        Args:
            name: Human-readable rule name
            group_by_column: Column to group records by
            compare_column: Column to check for variations within groups
            comparison_parameter: Type of comparison to perform
            rule_id: Optional rule ID
            
        Returns:
            Rule configuration dictionary
        """
        if rule_id is None:
            rule_id = self._generate_rule_id()
        
        # Get parameter details
        param_info = self.comparison_parameters.get(comparison_parameter, self.comparison_parameters['same_group_different_values'])
        
        rule = {
            'id': rule_id,
            'name': name,
            'group_by': group_by_column,
            'compare': compare_column,
            'comparison_parameter': comparison_parameter,
            'logic_type': param_info['logic'],
            'created_at': pd.Timestamp.now().isoformat(),
            'active': True,
            'description': param_info['description'].format(group_by=group_by_column, compare=compare_column)
        }
        
        return rule
    
    def get_comparison_parameters(self) -> Dict[str, Dict[str, str]]:
        """
        Get available comparison parameters.
        
        Returns:
            Dictionary of comparison parameters with their details
        """
        return self.comparison_parameters
    
    def validate_rule(self, rule: Dict[str, Any], df_columns: List[str]) -> Dict[str, Any]:
        """
        Validate a rule configuration against available data columns.
        
        Args:
            rule: Rule configuration dictionary
            df_columns: List of available DataFrame columns
            
        Returns:
            Validation result dictionary
        """
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['name', 'group_by', 'compare']
        for field in required_fields:
            if field not in rule or not rule[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check if columns exist in data
        if 'group_by' in rule and rule['group_by'] not in df_columns:
            errors.append(f"Group by column '{rule['group_by']}' not found in data")
        
        if 'compare' in rule and rule['compare'] not in df_columns:
            errors.append(f"Compare column '{rule['compare']}' not found in data")
        
        # Check for same column used for both group_by and compare
        if ('group_by' in rule and 'compare' in rule and 
            rule['group_by'] == rule['compare']):
            errors.append("Group by and compare columns cannot be the same")
        
        # Check rule name length
        if 'name' in rule and len(rule['name']) > 100:
            warnings.append("Rule name is very long (>100 characters)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_rule_suggestions(self, df_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate suggested rules based on column names.
        
        Args:
            df_columns: List of DataFrame column names
            
        Returns:
            List of suggested rule configurations
        """
        suggestions = []
        
        # Common patterns to look for
        patterns = {
            'ic': ['ic', 'nric', 'identity', 'id_number', 'identification'],
            'bank': ['bank', 'account', 'acc_no', 'account_number', 'bank_account'],
            'name': ['name', 'full_name', 'customer_name', 'beneficiary'],
            'phone': ['phone', 'mobile', 'contact', 'telephone'],
            'address': ['address', 'addr', 'location', 'residence'],
            'amount': ['amount', 'value', 'payment', 'sum', 'total']
        }
        
        # Find matching columns
        matched_columns = {}
        for pattern_type, keywords in patterns.items():
            matched_columns[pattern_type] = []
            for col in df_columns:
                col_lower = col.lower()
                for keyword in keywords:
                    if keyword in col_lower:
                        matched_columns[pattern_type].append(col)
                        break
        
        # Generate suggestions based on common fraud patterns
        fraud_patterns = [
            ('ic', 'bank', 'Same IC → Different Bank Account'),
            ('bank', 'ic', 'Same Bank Account → Different IC'),
            ('bank', 'name', 'Same Bank Account → Different Name'),
            ('ic', 'name', 'Same IC → Different Name'),
            ('name', 'bank', 'Same Name → Different Bank Account'),
            ('ic', 'phone', 'Same IC → Different Phone'),
            ('ic', 'address', 'Same IC → Different Address')
        ]
        
        for group_pattern, compare_pattern, rule_name in fraud_patterns:
            if (matched_columns.get(group_pattern) and 
                matched_columns.get(compare_pattern)):
                
                for group_col in matched_columns[group_pattern]:
                    for compare_col in matched_columns[compare_pattern]:
                        suggestions.append({
                            'name': rule_name.replace('IC', group_col).replace('Bank Account', compare_col),
                            'group_by': group_col,
                            'compare': compare_col,
                            'confidence': 'high',
                            'pattern_type': f"{group_pattern}_to_{compare_pattern}"
                        })
        
        # Remove duplicates and limit suggestions
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            key = (suggestion['group_by'], suggestion['compare'])
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:10]  # Limit to top 10 suggestions
    
    def export_rules(self, rules: List[Dict[str, Any]]) -> str:
        """
        Export rules to JSON string.
        
        Args:
            rules: List of rule configurations
            
        Returns:
            JSON string representation of rules
        """
        export_data = {
            'version': '1.0',
            'exported_at': pd.Timestamp.now().isoformat(),
            'rules': rules
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_rules(self, json_string: str) -> List[Dict[str, Any]]:
        """
        Import rules from JSON string.
        
        Args:
            json_string: JSON string containing rule configurations
            
        Returns:
            List of imported rule configurations
        """
        try:
            data = json.loads(json_string)
            
            if 'rules' not in data:
                raise ValueError("Invalid rule file format: missing 'rules' key")
            
            rules = data['rules']
            
            # Validate each rule
            valid_rules = []
            for rule in rules:
                if self._is_valid_rule_structure(rule):
                    # Regenerate ID to avoid conflicts
                    rule['id'] = self._generate_rule_id()
                    rule['imported_at'] = pd.Timestamp.now().isoformat()
                    valid_rules.append(rule)
            
            return valid_rules
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error importing rules: {str(e)}")
    
    def get_rule_statistics(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about configured rules.
        
        Args:
            rules: List of rule configurations
            
        Returns:
            Statistics dictionary
        """
        if not rules:
            return {
                'total_rules': 0,
                'active_rules': 0,
                'most_common_group_by': None,
                'most_common_compare': None,
                'rule_types': {}
            }
        
        active_rules = [r for r in rules if r.get('active', True)]
        
        # Count column usage
        group_by_counts = {}
        compare_counts = {}
        
        for rule in active_rules:
            group_by = rule.get('group_by')
            compare = rule.get('compare')
            
            if group_by:
                group_by_counts[group_by] = group_by_counts.get(group_by, 0) + 1
            if compare:
                compare_counts[compare] = compare_counts.get(compare, 0) + 1
        
        return {
            'total_rules': len(rules),
            'active_rules': len(active_rules),
            'most_common_group_by': max(group_by_counts.items(), key=lambda x: x[1])[0] if group_by_counts else None,
            'most_common_compare': max(compare_counts.items(), key=lambda x: x[1])[0] if compare_counts else None,
            'group_by_usage': group_by_counts,
            'compare_usage': compare_counts
        }
    
    def _generate_rule_id(self) -> int:
        """Generate a unique rule ID."""
        import time
        return int(time.time() * 1000) % 1000000
    
    def _is_valid_rule_structure(self, rule: Dict[str, Any]) -> bool:
        """Check if rule has valid structure."""
        required_fields = ['name', 'group_by', 'compare']
        return all(field in rule and rule[field] for field in required_fields)
    
    def clone_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a copy of an existing rule with new ID.
        
        Args:
            rule: Rule to clone
            
        Returns:
            Cloned rule with new ID
        """
        cloned_rule = rule.copy()
        cloned_rule['id'] = self._generate_rule_id()
        cloned_rule['name'] = f"{rule['name']} (Copy)"
        cloned_rule['created_at'] = pd.Timestamp.now().isoformat()
        
        return cloned_rule
    
    def update_rule(self, rule: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing rule with new values.
        
        Args:
            rule: Original rule
            updates: Dictionary of updates to apply
            
        Returns:
            Updated rule
        """
        updated_rule = rule.copy()
        updated_rule.update(updates)
        updated_rule['updated_at'] = pd.Timestamp.now().isoformat()
        
        return updated_rule