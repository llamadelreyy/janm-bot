import pandas as pd
import polars as pl
from typing import Tuple, Dict, Any
import io
import os

class FileProcessor:
    """Handles file upload, parsing, and validation for Excel and CSV files."""
    
    def __init__(self):
        self.max_rows = 200000
        self.max_columns = 100  # Increased to support 50+ columns as per requirements
        self.max_file_size = 200 * 1024 * 1024  # 200MB
    
    def process_file(self, uploaded_file) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process uploaded file and return DataFrame with file information.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (DataFrame, file_info_dict)
        """
        # Validate file size
        file_size = uploaded_file.size
        if file_size > self.max_file_size:
            raise ValueError(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (200MB)")
        
        # Get file extension
        file_name = uploaded_file.name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Read file based on extension
        try:
            if file_extension in ['.xlsx', '.xls']:
                df = self._read_excel(uploaded_file)
            elif file_extension == '.csv':
                df = self._read_csv(uploaded_file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Validate data dimensions
            self._validate_dimensions(df)
            
            # Clean and prepare data
            df = self._clean_data(df)
            
            # Generate file information
            file_info = {
                'name': file_name,
                'size': self._format_file_size(file_size),
                'rows': len(df),
                'columns': len(df.columns),
                'extension': file_extension
            }
            
            return df, file_info
            
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
    
    def _read_excel(self, uploaded_file) -> pd.DataFrame:
        """Read Excel file with optimized settings."""
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Read with pandas for better Excel support
            df = pd.read_excel(
                uploaded_file,
                engine='openpyxl',
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                keep_default_na=True
            )
            
            return df
            
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def _read_csv(self, uploaded_file) -> pd.DataFrame:
        """Read CSV file with automatic delimiter detection."""
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Try to detect delimiter
            sample = uploaded_file.read(1024).decode('utf-8')
            uploaded_file.seek(0)
            
            # Common delimiters to try
            delimiters = [',', ';', '\t', '|']
            best_delimiter = ','
            max_columns = 0
            
            for delimiter in delimiters:
                column_count = sample.count(delimiter)
                if column_count > max_columns:
                    max_columns = column_count
                    best_delimiter = delimiter
            
            # Read CSV with detected delimiter
            df = pd.read_csv(
                uploaded_file,
                delimiter=best_delimiter,
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                keep_default_na=True,
                encoding='utf-8'
            )
            
            return df
            
        except UnicodeDecodeError:
            # Try with different encoding
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file,
                delimiter=best_delimiter,
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                keep_default_na=True,
                encoding='latin-1'
            )
            return df
            
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
    
    def _validate_dimensions(self, df: pd.DataFrame):
        """Validate DataFrame dimensions against limits."""
        if len(df) > self.max_rows:
            raise ValueError(f"File has {len(df):,} rows, which exceeds the maximum of {self.max_rows:,} rows")
        
        if len(df.columns) > self.max_columns:
            raise ValueError(f"File has {len(df.columns)} columns, which exceeds the maximum of {self.max_columns} columns")
        
        if len(df) == 0:
            raise ValueError("File appears to be empty")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for analysis."""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Clean column names
        df.columns = df.columns.astype(str)
        df.columns = [col.strip() for col in df.columns]
        
        # Handle duplicate column names
        cols = df.columns.tolist()
        seen = set()
        for i, col in enumerate(cols):
            if col in seen:
                counter = 1
                new_col = f"{col}_{counter}"
                while new_col in seen:
                    counter += 1
                    new_col = f"{col}_{counter}"
                cols[i] = new_col
            seen.add(cols[i])
        df.columns = cols
        
        # Convert object columns to string for consistency
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str)
        
        return df
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def get_column_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed information about DataFrame columns."""
        column_info = {}
        
        for col in df.columns:
            column_info[col] = {
                'dtype': str(df[col].dtype),
                'non_null_count': df[col].count(),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique(),
                'sample_values': df[col].dropna().head(5).tolist()
            }
        
        return column_info