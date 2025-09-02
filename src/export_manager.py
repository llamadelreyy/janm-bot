import pandas as pd
import numpy as np
from io import BytesIO
import xlsxwriter
from typing import Dict, Any, Optional

class ExportManager:
    """Handles data export functionality for clean and flagged data."""
    
    def __init__(self):
        self.highlight_color = '#FFFF00'  # Yellow for flagged rows
        self.comment_color = '#FF6B6B'    # Red for violation comments
    
    def create_excel_with_highlights(self, 
                                   original_data: pd.DataFrame, 
                                   flagged_data: pd.DataFrame,
                                   analysis_results: Dict[str, Any]) -> BytesIO:
        """
        Create Excel file with flagged rows highlighted and comments.
        
        Args:
            original_data: Original DataFrame
            flagged_data: DataFrame with flagged rows
            analysis_results: Analysis results from fraud detection
            
        Returns:
            BytesIO object containing Excel file
        """
        output = BytesIO()
        
        # Create workbook and worksheet
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Define formats
        highlight_format = workbook.add_format({
            'bg_color': self.highlight_color,
            'border': 1
        })
        
        normal_format = workbook.add_format({
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })
        
        # Create main data worksheet
        worksheet = workbook.add_worksheet('Data_with_Flags')
        
        # Write headers
        for col_num, column in enumerate(original_data.columns):
            worksheet.write(0, col_num, column, header_format)
        
        # Add violation details column
        violation_col = len(original_data.columns)
        worksheet.write(0, violation_col, 'Violation_Details', header_format)
        
        # Create flagged rows lookup for faster processing
        flagged_lookup = set()
        violation_details = {}
        
        if len(flagged_data) > 0:
            # Create unique identifier for each row to match flagged data
            for idx, row in flagged_data.iterrows():
                # Create a tuple of values to identify the row
                row_key = tuple(row[col] for col in original_data.columns if col in row.index)
                flagged_lookup.add(row_key)
                
                # Store violation details
                if 'violation_details' in row.index:
                    violation_details[row_key] = row['violation_details']
                elif 'violation_reason' in row.index:
                    violation_details[row_key] = row['violation_reason']
                else:
                    violation_details[row_key] = "Flagged by fraud detection"
        
        # Write data rows
        for row_num, (idx, row) in enumerate(original_data.iterrows(), start=1):
            row_key = tuple(row[col] for col in original_data.columns)
            is_flagged = row_key in flagged_lookup
            
            # Choose format based on whether row is flagged
            row_format = highlight_format if is_flagged else normal_format
            
            # Write data cells
            for col_num, value in enumerate(row):
                # Handle different data types
                if pd.isna(value):
                    worksheet.write(row_num, col_num, '', row_format)
                elif isinstance(value, (int, float)):
                    worksheet.write(row_num, col_num, value, row_format)
                else:
                    worksheet.write(row_num, col_num, str(value), row_format)
            
            # Write violation details
            if is_flagged and row_key in violation_details:
                worksheet.write(row_num, violation_col, violation_details[row_key], row_format)
            else:
                worksheet.write(row_num, violation_col, '', row_format)
        
        # Auto-adjust column widths
        for col_num, column in enumerate(list(original_data.columns) + ['Violation_Details']):
            max_length = max(
                len(str(column)),
                original_data[column].astype(str).str.len().max() if column in original_data.columns else 20
            )
            worksheet.set_column(col_num, col_num, min(max_length + 2, 50))
        
        # Create summary worksheet
        self._create_summary_worksheet(workbook, analysis_results)
        
        # Create flagged data only worksheet
        if len(flagged_data) > 0:
            self._create_flagged_only_worksheet(workbook, flagged_data)
        
        workbook.close()
        output.seek(0)
        
        return output
    
    def create_clean_excel(self, clean_data: pd.DataFrame) -> BytesIO:
        """
        Create Excel file with only clean (unflagged) data.
        
        Args:
            clean_data: DataFrame with clean data only
            
        Returns:
            BytesIO object containing Excel file
        """
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            clean_data.to_excel(writer, sheet_name='Clean_Data', index=False)
            
            # Get workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Clean_Data']
            
            # Format headers
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D3D3D3',
                'border': 1
            })
            
            for col_num, column in enumerate(clean_data.columns):
                worksheet.write(0, col_num, column, header_format)
            
            # Auto-adjust column widths
            for col_num, column in enumerate(clean_data.columns):
                max_length = max(
                    len(str(column)),
                    clean_data[column].astype(str).str.len().max()
                )
                worksheet.set_column(col_num, col_num, min(max_length + 2, 50))
        
        output.seek(0)
        return output
    
    def create_csv_export(self, data: pd.DataFrame) -> str:
        """
        Create CSV string from DataFrame.
        
        Args:
            data: DataFrame to export
            
        Returns:
            CSV string
        """
        return data.to_csv(index=False)
    
    def _create_summary_worksheet(self, workbook, analysis_results: Dict[str, Any]):
        """Create summary worksheet with analysis results."""
        worksheet = workbook.add_worksheet('Analysis_Summary')
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#4472C4',
            'font_color': 'white'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3'
        })
        
        # Write title
        worksheet.write(0, 0, 'Fraud Detection Analysis Summary', title_format)
        worksheet.merge_range(0, 0, 0, 3, 'Fraud Detection Analysis Summary', title_format)
        
        # Write overall statistics
        row = 2
        worksheet.write(row, 0, 'Overall Statistics', header_format)
        row += 1
        
        stats = [
            ('Total Rows Analyzed', analysis_results.get('total_rows', 0)),
            ('Total Flagged Rows', analysis_results.get('total_flagged', 0)),
            ('Overall Flag Rate', f"{analysis_results.get('overall_flag_rate', 0):.2%}"),
            ('Rules Applied', analysis_results.get('rules_count', 0))
        ]
        
        for stat_name, stat_value in stats:
            worksheet.write(row, 0, stat_name)
            worksheet.write(row, 1, stat_value)
            row += 1
        
        # Write rule-specific results
        row += 2
        worksheet.write(row, 0, 'Rule Results', header_format)
        row += 1
        
        # Headers for rule results
        rule_headers = ['Rule Name', 'Flagged Rows', 'Flag Rate', 'Flagged Groups']
        for col, header in enumerate(rule_headers):
            worksheet.write(row, col, header, header_format)
        row += 1
        
        # Rule data
        for rule_result in analysis_results.get('rule_results', []):
            if rule_result.get('success', False):
                worksheet.write(row, 0, rule_result.get('rule_name', ''))
                worksheet.write(row, 1, rule_result.get('flagged_count', 0))
                worksheet.write(row, 2, f"{rule_result.get('flag_rate', 0):.2%}")
                worksheet.write(row, 3, rule_result.get('flagged_groups', 0))
                row += 1
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 3, 15)
    
    def _create_flagged_only_worksheet(self, workbook, flagged_data: pd.DataFrame):
        """Create worksheet with only flagged data."""
        worksheet = workbook.add_worksheet('Flagged_Data_Only')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FF6B6B',
            'font_color': 'white',
            'border': 1
        })
        
        flagged_format = workbook.add_format({
            'bg_color': '#FFE6E6',
            'border': 1
        })
        
        # Write headers
        for col_num, column in enumerate(flagged_data.columns):
            worksheet.write(0, col_num, column, header_format)
        
        # Write flagged data
        for row_num, (idx, row) in enumerate(flagged_data.iterrows(), start=1):
            for col_num, value in enumerate(row):
                if pd.isna(value):
                    worksheet.write(row_num, col_num, '', flagged_format)
                elif isinstance(value, (int, float)):
                    worksheet.write(row_num, col_num, value, flagged_format)
                else:
                    worksheet.write(row_num, col_num, str(value), flagged_format)
        
        # Auto-adjust column widths
        for col_num, column in enumerate(flagged_data.columns):
            if column in flagged_data.columns:
                max_length = max(
                    len(str(column)),
                    flagged_data[column].astype(str).str.len().max()
                )
                worksheet.set_column(col_num, col_num, min(max_length + 2, 50))
    
    def get_export_filename(self, base_name: str, export_type: str, file_format: str) -> str:
        """
        Generate appropriate filename for export.
        
        Args:
            base_name: Base filename from original upload
            export_type: Type of export ('clean', 'flagged', 'highlighted')
            file_format: File format ('xlsx', 'csv')
            
        Returns:
            Generated filename
        """
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Remove extension from base name
        if '.' in base_name:
            base_name = base_name.rsplit('.', 1)[0]
        
        return f"{base_name}_{export_type}_{timestamp}.{file_format}"