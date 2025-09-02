import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple

class FraudDetector:
    """Core fraud detection engine for group-based analysis."""
    
    def __init__(self):
        self.results_cache = {}
    
    def preview_rule(self, df: pd.DataFrame, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview a single rule without full analysis.
        
        Args:
            df: Input DataFrame
            rule: Rule configuration dict
            
        Returns:
            Preview results dictionary
        """
        group_by_col = rule['group_by']
        compare_col = rule['compare']
        comparison_parameter = rule.get('comparison_parameter', 'same_group_different_values')
        
        # Apply the appropriate logic based on comparison parameter
        if comparison_parameter == 'same_group_different_values':
            return self._preview_same_group_different_values(df, group_by_col, compare_col)
        elif comparison_parameter == 'different_group_same_values':
            return self._preview_different_group_same_values(df, group_by_col, compare_col)
        elif comparison_parameter == 'direct_column_mismatch':
            return self._preview_direct_column_mismatch(df, group_by_col, compare_col)
        else:
            # Default to original behavior
            return self._preview_same_group_different_values(df, group_by_col, compare_col)
    
    def _preview_same_group_different_values(self, df: pd.DataFrame, group_by_col: str, compare_col: str) -> Dict[str, Any]:
        """Preview for same group → different values logic."""
        # Group by the specified column and count unique values in compare column
        grouped = df.groupby(group_by_col)[compare_col].nunique().reset_index()
        grouped.columns = [group_by_col, 'unique_count']
        
        # Find groups with more than 1 unique value (violations)
        flagged_groups = grouped[grouped['unique_count'] > 1]
        
        # Count flagged rows
        flagged_rows = 0
        if len(flagged_groups) > 0:
            flagged_values = flagged_groups[group_by_col].tolist()
            flagged_rows = len(df[df[group_by_col].isin(flagged_values)])
        
        return {
            'total_groups': len(grouped),
            'flagged_groups': len(flagged_groups),
            'flagged_rows': flagged_rows,
            'flag_rate': flagged_rows / len(df) if len(df) > 0 else 0
        }
    
    def _preview_different_group_same_values(self, df: pd.DataFrame, group_by_col: str, compare_col: str) -> Dict[str, Any]:
        """Preview for different groups → same values logic."""
        # Group by compare column and count unique values in group_by column
        grouped = df.groupby(compare_col)[group_by_col].nunique().reset_index()
        grouped.columns = [compare_col, 'unique_count']
        
        # Find compare values shared by multiple groups (violations)
        flagged_values = grouped[grouped['unique_count'] > 1]
        
        # Count flagged rows
        flagged_rows = 0
        if len(flagged_values) > 0:
            flagged_compare_values = flagged_values[compare_col].tolist()
            flagged_rows = len(df[df[compare_col].isin(flagged_compare_values)])
        
        return {
            'total_groups': len(grouped),
            'flagged_groups': len(flagged_values),
            'flagged_rows': flagged_rows,
            'flag_rate': flagged_rows / len(df) if len(df) > 0 else 0
        }
    
    def _preview_direct_column_mismatch(self, df: pd.DataFrame, group_by_col: str, compare_col: str) -> Dict[str, Any]:
        """Preview for direct column mismatch logic."""
        # Compare columns directly row by row
        mismatched_rows = df[df[group_by_col] != df[compare_col]]
        
        return {
            'total_groups': len(df),
            'flagged_groups': len(mismatched_rows),
            'flagged_rows': len(mismatched_rows),
            'flag_rate': len(mismatched_rows) / len(df) if len(df) > 0 else 0
        }
    
    def analyze_single_rule(self, df: pd.DataFrame, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single fraud detection rule.
        
        Args:
            df: Input DataFrame
            rule: Rule configuration dict
            
        Returns:
            Analysis results for the rule
        """
        group_by_col = rule['group_by']
        compare_col = rule['compare']
        rule_name = rule['name']
        comparison_parameter = rule.get('comparison_parameter', 'same_group_different_values')
        
        try:
            # Ensure columns exist
            if group_by_col not in df.columns:
                raise ValueError(f"Group by column '{group_by_col}' not found in data")
            if compare_col not in df.columns:
                raise ValueError(f"Compare column '{compare_col}' not found in data")
            
            # Remove rows where either column is null
            clean_df = df.dropna(subset=[group_by_col, compare_col])
            
            if len(clean_df) == 0:
                return self._empty_result(rule_name)
            
            # Apply the appropriate analysis logic based on comparison parameter
            if comparison_parameter == 'same_group_different_values':
                return self._analyze_same_group_different_values(clean_df, rule, group_by_col, compare_col, rule_name)
            elif comparison_parameter == 'different_group_same_values':
                return self._analyze_different_group_same_values(clean_df, rule, group_by_col, compare_col, rule_name)
            elif comparison_parameter == 'direct_column_mismatch':
                return self._analyze_direct_column_mismatch(clean_df, rule, group_by_col, compare_col, rule_name)
            else:
                # Default to original behavior
                return self._analyze_same_group_different_values(clean_df, rule, group_by_col, compare_col, rule_name)
            
        except Exception as e:
            return {
                'rule_name': rule_name,
                'rule_config': rule,
                'error': str(e),
                'success': False,
                'flagged_count': 0,
                'flag_rate': 0,
                'flagged_data': pd.DataFrame()
            }
    
    def _analyze_same_group_different_values(self, clean_df: pd.DataFrame, rule: Dict[str, Any],
                                           group_by_col: str, compare_col: str, rule_name: str) -> Dict[str, Any]:
        """
        Analyze same group → different values logic.
        
        Example: Bank 1111 has multiple ICs (021, 031):
        - Row 1: Bank 1111, IC 021 (flagged - part of violating group)
        - Row 2: Bank 1111, IC 031 (flagged - part of violating group)
        - Row 3: Bank 1111, IC 021 (flagged but deduplicated in results)
        
        All rows belonging to groups with multiple different values are flagged,
        but results show only unique combinations.
        """
        # Group by the specified column and analyze variations
        grouped = clean_df.groupby(group_by_col)[compare_col].agg(['nunique', 'unique']).reset_index()
        grouped.columns = [group_by_col, 'unique_count', 'unique_values']
        
        # Find groups with violations (more than 1 unique value in compare column)
        violations = grouped[grouped['unique_count'] > 1].copy()
        
        if len(violations) == 0:
            return self._empty_result(rule_name)
        
        # Get ALL rows that belong to violating groups
        flagged_group_values = violations[group_by_col].tolist()
        all_flagged_rows = clean_df[clean_df[group_by_col].isin(flagged_group_values)].copy()
        
        # For results display, show only unique combinations to avoid duplicates
        flagged_data = all_flagged_rows.drop_duplicates(subset=[group_by_col, compare_col], keep='first')
        
        # Add violation details to flagged data
        flagged_data['violation_reason'] = f"Rule: {rule_name}"
        flagged_data['violation_details'] = flagged_data.apply(
            lambda row: self._get_violation_details_same_group(row, group_by_col, compare_col, violations),
            axis=1
        )
        
        # Calculate statistics
        total_rows = len(clean_df)
        flagged_count = len(flagged_data)
        flag_rate = flagged_count / total_rows if total_rows > 0 else 0
        
        return {
            'rule_name': rule_name,
            'rule_config': rule,
            'total_rows_analyzed': total_rows,
            'flagged_count': flagged_count,
            'flag_rate': flag_rate,
            'flagged_groups': len(violations),
            'total_groups': len(grouped),
            'flagged_data': flagged_data,
            'violation_summary': self._create_violation_summary_same_group(violations, group_by_col, compare_col),
            'success': True
        }
    
    def _analyze_different_group_same_values(self, clean_df: pd.DataFrame, rule: Dict[str, Any],
                                           group_by_col: str, compare_col: str, rule_name: str) -> Dict[str, Any]:
        """
        Analyze different groups → same values logic.
        
        Example: Bank 7676 is used by multiple ICs (111, 222):
        - Row 1: IC 111, Bank 7676 (flagged - part of violating value)
        - Row 2: IC 222, Bank 7676 (flagged - part of violating value)
        - Row 3: IC 111, Bank 7676 (flagged but deduplicated in results)
        
        All rows belonging to values shared by multiple groups are flagged,
        but results show only unique combinations.
        """
        # Group by compare column and analyze which groups share the same value
        grouped = clean_df.groupby(compare_col)[group_by_col].agg(['nunique', 'unique']).reset_index()
        grouped.columns = [compare_col, 'unique_count', 'unique_groups']
        
        # Find compare values shared by multiple groups (violations)
        violations = grouped[grouped['unique_count'] > 1].copy()
        
        if len(violations) == 0:
            return self._empty_result(rule_name)
        
        # Get ALL rows that belong to violating compare values
        flagged_compare_values = violations[compare_col].tolist()
        all_flagged_rows = clean_df[clean_df[compare_col].isin(flagged_compare_values)].copy()
        
        # For results display, show only unique combinations to avoid duplicates
        flagged_data = all_flagged_rows.drop_duplicates(subset=[group_by_col, compare_col], keep='first')
        
        # Add violation details to flagged data
        flagged_data['violation_reason'] = f"Rule: {rule_name}"
        flagged_data['violation_details'] = flagged_data.apply(
            lambda row: self._get_violation_details_different_group(row, group_by_col, compare_col, violations),
            axis=1
        )
        
        # Calculate statistics
        total_rows = len(clean_df)
        flagged_count = len(flagged_data)
        flag_rate = flagged_count / total_rows if total_rows > 0 else 0
        
        return {
            'rule_name': rule_name,
            'rule_config': rule,
            'total_rows_analyzed': total_rows,
            'flagged_count': flagged_count,
            'flag_rate': flag_rate,
            'flagged_groups': len(violations),
            'total_groups': len(grouped),
            'flagged_data': flagged_data,
            'violation_summary': self._create_violation_summary_different_group(violations, group_by_col, compare_col),
            'success': True
        }
    
    def _analyze_direct_column_mismatch(self, clean_df: pd.DataFrame, rule: Dict[str, Any],
                                      group_by_col: str, compare_col: str, rule_name: str) -> Dict[str, Any]:
        """Analyze direct column mismatch logic."""
        # Compare columns directly row by row
        flagged_data = clean_df[clean_df[group_by_col] != clean_df[compare_col]].copy()
        
        if len(flagged_data) == 0:
            return self._empty_result(rule_name)
        
        # Add violation details to flagged data
        flagged_data['violation_reason'] = f"Rule: {rule_name}"
        flagged_data['violation_details'] = flagged_data.apply(
            lambda row: f"{group_by_col} '{row[group_by_col]}' ≠ {compare_col} '{row[compare_col]}'",
            axis=1
        )
        
        # Calculate statistics
        total_rows = len(clean_df)
        flagged_count = len(flagged_data)
        flag_rate = flagged_count / total_rows if total_rows > 0 else 0
        
        return {
            'rule_name': rule_name,
            'rule_config': rule,
            'total_rows_analyzed': total_rows,
            'flagged_count': flagged_count,
            'flag_rate': flag_rate,
            'flagged_groups': flagged_count,  # Each row is its own "group" in this case
            'total_groups': total_rows,
            'flagged_data': flagged_data,
            'violation_summary': [],  # No group-based summary for direct comparison
            'success': True
        }
    
    def analyze_all_rules(self, df: pd.DataFrame, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all configured rules and combine results.
        
        Args:
            df: Input DataFrame
            rules: List of rule configuration dicts
            
        Returns:
            Combined analysis results
        """
        if not rules:
            return {
                'rule_results': [],
                'total_flagged': 0,
                'overall_flag_rate': 0,
                'combined_flagged_data': pd.DataFrame(),
                'success': True
            }
        
        rule_results = []
        all_flagged_data = []
        
        # Analyze each rule
        for rule in rules:
            result = self.analyze_single_rule(df, rule)
            rule_results.append(result)
            
            if result['success'] and len(result['flagged_data']) > 0:
                all_flagged_data.append(result['flagged_data'])
        
        # Combine all flagged data
        if all_flagged_data:
            combined_flagged = pd.concat(all_flagged_data, ignore_index=True)
            # Remove duplicates (same row flagged by multiple rules)
            # Use all original columns except violation-related columns for duplicate detection
            original_columns = [col for col in df.columns.tolist() if col in combined_flagged.columns]
            combined_flagged = combined_flagged.drop_duplicates(subset=original_columns, keep='first')
        else:
            combined_flagged = pd.DataFrame()
        
        total_flagged = len(combined_flagged)
        overall_flag_rate = total_flagged / len(df) if len(df) > 0 else 0
        
        return {
            'rule_results': rule_results,
            'total_flagged': total_flagged,
            'overall_flag_rate': overall_flag_rate,
            'combined_flagged_data': combined_flagged,
            'total_rows': len(df),
            'rules_count': len(rules),
            'success': True
        }
    
    def _empty_result(self, rule_name: str) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'rule_name': rule_name,
            'total_rows_analyzed': 0,
            'flagged_count': 0,
            'flag_rate': 0,
            'flagged_groups': 0,
            'total_groups': 0,
            'flagged_data': pd.DataFrame(),
            'violation_summary': [],
            'success': True
        }
    
    def _get_violation_details_same_group(self, row: pd.Series, group_by_col: str, compare_col: str, violations: pd.DataFrame) -> str:
        """Generate detailed violation description for same group → different values."""
        group_value = row[group_by_col]
        violation_info = violations[violations[group_by_col] == group_value]
        
        if len(violation_info) > 0:
            unique_values = violation_info.iloc[0]['unique_values']
            return f"Group '{group_value}' has {len(unique_values)} different values: {', '.join(map(str, unique_values))}"
        
        return "Violation detected"
    
    def _get_violation_details_different_group(self, row: pd.Series, group_by_col: str, compare_col: str, violations: pd.DataFrame) -> str:
        """Generate detailed violation description for different groups → same values."""
        compare_value = row[compare_col]
        violation_info = violations[violations[compare_col] == compare_value]
        
        if len(violation_info) > 0:
            unique_groups = violation_info.iloc[0]['unique_groups']
            return f"Value '{compare_value}' is shared by {len(unique_groups)} different groups: {', '.join(map(str, unique_groups))}"
        
        return "Violation detected"
    
    # Keep original method for backward compatibility
    def _get_violation_details(self, row: pd.Series, group_by_col: str, compare_col: str, violations: pd.DataFrame) -> str:
        """Generate detailed violation description for a row (backward compatibility)."""
        return self._get_violation_details_same_group(row, group_by_col, compare_col, violations)
    
    def _create_violation_summary_same_group(self, violations: pd.DataFrame, group_by_col: str, compare_col: str) -> List[Dict[str, Any]]:
        """Create a summary of violations for same group → different values."""
        summary = []
        
        for _, row in violations.iterrows():
            group_value = row[group_by_col]
            unique_values = row['unique_values']
            unique_count = row['unique_count']
            
            summary.append({
                'group_value': group_value,
                'unique_count': unique_count,
                'unique_values': list(unique_values),
                'severity': self._calculate_severity(unique_count)
            })
        
        # Sort by severity (highest first)
        summary.sort(key=lambda x: x['unique_count'], reverse=True)
        
        return summary
    
    def _create_violation_summary_different_group(self, violations: pd.DataFrame, group_by_col: str, compare_col: str) -> List[Dict[str, Any]]:
        """Create a summary of violations for different groups → same values."""
        summary = []
        
        for _, row in violations.iterrows():
            compare_value = row[compare_col]
            unique_groups = row['unique_groups']
            unique_count = row['unique_count']
            
            summary.append({
                'shared_value': compare_value,
                'group_count': unique_count,
                'groups': list(unique_groups),
                'severity': self._calculate_severity(unique_count)
            })
        
        # Sort by severity (highest first)
        summary.sort(key=lambda x: x['group_count'], reverse=True)
        
        return summary
    
    # Keep original method for backward compatibility
    def _create_violation_summary(self, violations: pd.DataFrame, group_by_col: str, compare_col: str) -> List[Dict[str, Any]]:
        """Create a summary of violations for reporting (backward compatibility)."""
        return self._create_violation_summary_same_group(violations, group_by_col, compare_col)
    
    def _calculate_severity(self, unique_count: int) -> str:
        """Calculate violation severity based on unique count."""
        if unique_count >= 5:
            return "High"
        elif unique_count >= 3:
            return "Medium"
        else:
            return "Low"
    
    def get_clean_data(self, df: pd.DataFrame, flagged_data: pd.DataFrame) -> pd.DataFrame:
        """
        Get clean data by removing flagged rows.
        
        Args:
            df: Original DataFrame
            flagged_data: DataFrame containing flagged rows
            
        Returns:
            Clean DataFrame without flagged rows
        """
        if len(flagged_data) == 0:
            return df.copy()
        
        # Create a unique identifier for each row
        df_with_index = df.reset_index(drop=True)
        df_with_index['_temp_index'] = df_with_index.index
        
        flagged_with_index = flagged_data.reset_index(drop=True)
        
        # Find matching rows (excluding violation columns added by analysis)
        original_columns = [col for col in df.columns if col in flagged_data.columns]
        
        # Merge to find flagged indices
        merged = df_with_index.merge(
            flagged_with_index[original_columns],
            on=original_columns,
            how='inner'
        )
        
        flagged_indices = merged['_temp_index'].unique()
        
        # Return clean data
        clean_data = df_with_index[~df_with_index['_temp_index'].isin(flagged_indices)]
        clean_data = clean_data.drop('_temp_index', axis=1)
        
        return clean_data