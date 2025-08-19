# Custom Fraud Detection System

A web-based fraud detection system built with Streamlit for analyzing government payment Excel data. The system enables auditors to upload large Excel files and define dynamic, column-based rules for fraud detection.

## 🎯 Features

### Phase 1 (POC) - Implemented
- **Excel Upload & Parsing**: Support for .xlsx, .xls, and .csv files (up to 200,000 rows, 100 columns)
- **Auto-header Detection**: Automatically detects column headers and data types
- **Flexible Rule-Based Comparison**: Create dynamic rules like "Same IC → Different Bank Account"
- **Group-Based Analysis**: Advanced fraud detection using group-by logic
- **Visual Analysis Output**: Charts and metrics showing fraud patterns
- **Export Functionality**: Download clean data and highlighted flagged data
- **Performance Optimized**: Handles large files efficiently with Pandas/Polars

### Key Fraud Detection Rules Supported
- Same IC → Different Bank Account
- Same Bank Account → Different IC  
- Same Bank Account → Different Name
- Same IC → Different Name
- Custom group-by rules based on your data columns

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 📖 Usage Guide

### 1. Upload Data
- Navigate to "📁 Upload Data"
- Drag and drop or select your Excel/CSV file
- System supports files up to 200MB with 200,000+ rows and 100 columns
- View data preview and column information

### 2. Configure Rules
- Go to "⚙️ Configure Rules"
- Use suggested rules based on your column names, or
- Create custom rules by selecting:
  - **Group By Column**: Column to group records by (e.g., IC Number)
  - **Compare Column**: Column to check for variations (e.g., Bank Account)
- Preview rules before running full analysis

### 3. Run Analysis
- Visit "📊 Analysis Results"
- Click "🔍 Run Fraud Analysis"
- View summary metrics and visualizations
- Examine flagged records for each rule

### 4. Export Results
- Go to "📥 Export Data"
- Download options:
  - **Excel with Highlights**: Original data with flagged rows highlighted
  - **Clean Data**: Data with flagged rows removed (Excel/CSV)

## 🏗️ System Architecture

```
fraud-detection-system/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── src/
│   ├── __init__.py
│   ├── file_processor.py  # Excel/CSV parsing and validation
│   ├── fraud_detector.py  # Core fraud detection engine
│   ├── rule_engine.py     # Rule management and validation
│   └── export_manager.py  # Data export functionality
└── README.md
```

### Core Components

- **FileProcessor**: Handles file upload, parsing, and data validation
- **RuleEngine**: Manages fraud detection rules and provides suggestions
- **FraudDetector**: Implements group-based analysis algorithms
- **ExportManager**: Creates Excel files with highlights and clean data exports

## 🔧 Technical Details

### Supported File Formats
- **Excel**: `.xlsx`, `.xls`
- **CSV**: `.csv` (auto-delimiter detection)
- **Limits**: Up to 200MB, 200,000 rows, 100 columns

### Performance Features
- Efficient memory usage for large datasets
- Chunked processing for files approaching limits
- Optimized pandas operations
- Progress indicators for long-running operations

### Data Processing
- Automatic data type detection
- Missing value handling
- Duplicate column name resolution
- Data quality validation

## 📊 Sample Data

The system includes a sample data generator for testing:
1. Go to "📁 Upload Data"
2. Click "Generate Sample Data"
3. Test with pre-built fraud patterns

## 🛡️ Security & Privacy

- All processing happens locally on your machine
- No data is sent to external servers
- Files are processed in memory and not permanently stored
- Export files are generated client-side

## 🔍 Fraud Detection Logic

The system uses **group-based analysis**:

1. **Group By**: Records are grouped by a specified column (e.g., IC Number)
2. **Compare**: Within each group, check if another column has multiple unique values
3. **Flag**: If a group has >1 unique value in the compare column, flag all records in that group

### Example
**Rule**: Same IC → Different Bank Account
- Group all records by IC Number
- For each IC, check if there are multiple different bank accounts
- If yes, flag all records for that IC as potentially fraudulent

## 🚧 Future Enhancements (Phase 2)

- Scheduled uploads and automated checks
- Audit logging with timestamps
- Machine learning-based anomaly detection
- Advanced statistical analysis
- Multi-user support with role-based access

## 🐛 Troubleshooting

### Common Issues

**File Upload Errors:**
- Ensure file is under 200MB
- Check that first row contains headers
- Verify file format is supported

**Memory Issues:**
- Close other applications to free RAM
- Try processing smaller file chunks
- Use CSV format instead of Excel for very large files

**Rule Configuration:**
- Ensure selected columns exist in your data
- Group By and Compare columns must be different
- Check for missing values in key columns

## 📝 License

This project is provided as-is for educational and professional use.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your data format matches requirements
3. Test with the sample data generator first