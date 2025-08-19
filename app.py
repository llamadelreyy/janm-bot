import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import time
from typing import Dict, List, Tuple, Optional

# Import our custom modules
from src.file_processor import FileProcessor
from src.rule_engine import RuleEngine
from src.fraud_detector import FraudDetector
from src.export_manager import ExportManager

# Page configuration
st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🔍 Custom Fraud Detection System")
    st.markdown("**Analyze government payment data for fraud patterns**")
    
    # Initialize session state
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'file_info' not in st.session_state:
        st.session_state.file_info = None
    if 'rules' not in st.session_state:
        st.session_state.rules = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page:",
            ["📁 Upload Data", "⚙️ Configure Rules", "📊 Analysis Results", "📥 Export Data"]
        )
        
        # Show current status
        st.markdown("---")
        st.subheader("Current Status")
        
        if st.session_state.uploaded_data is not None:
            st.success(f"✅ Data loaded ({len(st.session_state.uploaded_data):,} rows)")
        else:
            st.warning("⚠️ No data uploaded")
        
        if st.session_state.rules:
            st.success(f"✅ {len(st.session_state.rules)} rules configured")
        else:
            st.warning("⚠️ No rules configured")
        
        if st.session_state.analysis_results:
            st.success("✅ Analysis completed")
        else:
            st.info("ℹ️ Analysis not run")
    
    # Main content based on selected page
    if page == "📁 Upload Data":
        upload_page()
    elif page == "⚙️ Configure Rules":
        rules_page()
    elif page == "📊 Analysis Results":
        analysis_page()
    elif page == "📥 Export Data":
        export_page()

def upload_page():
    st.header("📁 Data Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Excel or CSV File")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['xlsx', 'xls', 'csv'],
            help="Supports up to 200,000 rows and 50+ columns"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("Processing file..."):
                    processor = FileProcessor()
                    df, file_info = processor.process_file(uploaded_file)
                    
                    st.session_state.uploaded_data = df
                    st.session_state.file_info = file_info
                    
                    # Clear previous analysis results when new data is uploaded
                    st.session_state.analysis_results = None
                    
                    st.success("✅ Upload Successful!")
                    
                    # Display file information
                    st.subheader("File Information")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Rows", f"{file_info['rows']:,}")
                    with col_b:
                        st.metric("Columns", file_info['columns'])
                    with col_c:
                        st.metric("File Size", file_info['size'])
                    
                    # Show column headers
                    st.subheader("Detected Columns")
                    st.write(", ".join(df.columns.tolist()))
                    
                    # Preview data
                    st.subheader("Data Preview")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Data quality summary
                    st.subheader("Data Quality Summary")
                    quality_col1, quality_col2 = st.columns(2)
                    
                    with quality_col1:
                        st.write("**Missing Values by Column:**")
                        missing_data = df.isnull().sum()
                        missing_data = missing_data[missing_data > 0]
                        if len(missing_data) > 0:
                            st.dataframe(missing_data.to_frame('Missing Count'))
                        else:
                            st.write("No missing values found")
                    
                    with quality_col2:
                        st.write("**Data Types:**")
                        dtype_summary = df.dtypes.value_counts().to_frame('Count')
                        st.dataframe(dtype_summary)
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with col2:
        st.subheader("Upload Guidelines")
        st.info("""
        **Supported Formats:**
        - Excel (.xlsx, .xls)
        - CSV (.csv)
        
        **Limits:**
        - Up to 200,000 rows
        - Up to 100 columns
        - Max file size: 200MB
        
        **Requirements:**
        - First row should contain headers
        - Data should be clean and consistent
        """)
        
        # Sample data generator
        st.subheader("Need Sample Data?")
        if st.button("Generate Sample Data"):
            sample_df = generate_sample_data()
            st.session_state.uploaded_data = sample_df
            st.session_state.file_info = {
                'name': 'sample_data.csv',
                'size': '15.2 KB',
                'rows': len(sample_df),
                'columns': len(sample_df.columns),
                'extension': '.csv'
            }
            st.success("Sample data generated!")
            st.rerun()

def rules_page():
    st.header("⚙️ Configure Detection Rules")
    
    if st.session_state.uploaded_data is None:
        st.warning("Please upload data first!")
        return
    
    df = st.session_state.uploaded_data
    columns = df.columns.tolist()
    rule_engine = RuleEngine()
    
    # Show rule suggestions
    with st.expander("💡 Suggested Rules", expanded=False):
        suggestions = rule_engine.get_rule_suggestions(columns)
        if suggestions:
            st.write("Based on your column names, here are some suggested fraud detection rules:")
            for i, suggestion in enumerate(suggestions):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{suggestion['name']}**")
                    st.write(f"Group by: {suggestion['group_by']} → Compare: {suggestion['compare']}")
                with col2:
                    st.write(f"Confidence: {suggestion['confidence']}")
                with col3:
                    if st.button(f"Add Rule", key=f"suggest_{i}"):
                        rule = rule_engine.create_rule(
                            suggestion['name'],
                            suggestion['group_by'],
                            suggestion['compare']
                        )
                        st.session_state.rules.append(rule)
                        st.success(f"Rule '{suggestion['name']}' added!")
                        st.rerun()
        else:
            st.write("No automatic suggestions available for your data columns.")
    
    st.subheader("Create New Rule")
    
    with st.form("rule_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rule_name = st.text_input(
                "Rule Name",
                placeholder="e.g., Same IC → Different Bank Account"
            )
            group_by_column = st.selectbox(
                "Group By Column",
                columns,
                help="Column to group records by (e.g., IC Number)"
            )
        
        with col2:
            compare_column = st.selectbox(
                "Compare Column",
                columns,
                help="Column to check for variations within groups (e.g., Bank Account)"
            )
            
            # Get comparison parameters from rule engine
            comparison_params = rule_engine.get_comparison_parameters()
            comparison_parameter = st.selectbox(
                "Comparison Type",
                options=list(comparison_params.keys()),
                format_func=lambda x: comparison_params[x]['name'],
                help="Select the type of comparison to perform"
            )
        
        with col3:
            # Show parameter description and example
            if comparison_parameter:
                param_info = comparison_params[comparison_parameter]
                st.write("**Description:**")
                st.write(param_info['description'].format(group_by=group_by_column or '[Group By]', compare=compare_column or '[Compare]'))
                st.write("**Example:**")
                st.write(param_info['example'])
        
        submitted = st.form_submit_button("Add Rule")
        
        if submitted and rule_name and group_by_column and compare_column:
            # Validate rule
            temp_rule = {
                'name': rule_name,
                'group_by': group_by_column,
                'compare': compare_column,
                'comparison_parameter': comparison_parameter
            }
            validation = rule_engine.validate_rule(temp_rule, columns)
            
            if validation['valid']:
                rule = rule_engine.create_rule(rule_name, group_by_column, compare_column, comparison_parameter)
                st.session_state.rules.append(rule)
                st.success(f"Rule '{rule_name}' added successfully!")
                st.rerun()
            else:
                for error in validation['errors']:
                    st.error(error)
                for warning in validation['warnings']:
                    st.warning(warning)
    
    # Display existing rules
    if st.session_state.rules:
        st.subheader("Configured Rules")
        
        for i, rule in enumerate(st.session_state.rules):
            with st.expander(f"Rule {i+1}: {rule['name']}", expanded=True):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"**Group By:** {rule['group_by']}")
                with col2:
                    st.write(f"**Compare:** {rule['compare']}")
                with col3:
                    # Show comparison parameter if available
                    comparison_param = rule.get('comparison_parameter', 'same_group_different_values')
                    comparison_params = rule_engine.get_comparison_parameters()
                    param_name = comparison_params.get(comparison_param, {}).get('name', 'Same Group → Different Values')
                    st.write(f"**Type:** {param_name}")
                with col4:
                    if st.button("Preview", key=f"preview_{i}"):
                        with st.spinner("Analyzing..."):
                            detector = FraudDetector()
                            preview_results = detector.preview_rule(df, rule)
                            
                            st.write(f"**Preview Results:**")
                            st.write(f"- Groups analyzed: {preview_results['total_groups']}")
                            st.write(f"- Flagged groups: {preview_results['flagged_groups']}")
                            st.write(f"- Flagged rows: {preview_results['flagged_rows']}")
                            st.write(f"- Flag rate: {preview_results['flag_rate']:.2%}")
                
                with col5:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.rules.pop(i)
                        st.rerun()

def analysis_page():
    st.header("📊 Analysis Results")
    
    if st.session_state.uploaded_data is None:
        st.warning("Please upload data first!")
        return
    
    if not st.session_state.rules:
        st.warning("Please configure at least one rule!")
        return
    
    df = st.session_state.uploaded_data
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔍 Run Fraud Analysis", type="primary", use_container_width=True):
            with st.spinner("Running analysis..."):
                detector = FraudDetector()
                results = detector.analyze_all_rules(df, st.session_state.rules)
                st.session_state.analysis_results = results
                st.success("Analysis completed!")
                st.rerun()
    
    with col2:
        if st.session_state.analysis_results:
            st.write(f"Last analysis: {len(st.session_state.rules)} rules on {len(df):,} rows")
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Summary metrics
        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Flagged Rows", f"{results['total_flagged']:,}")
        with col3:
            st.metric("Flag Rate", f"{results['overall_flag_rate']:.2%}")
        with col4:
            st.metric("Rules Applied", len(st.session_state.rules))
        
        # Visualization
        st.subheader("Analysis Visualization")
        
        # Create flag rate chart
        rule_names = [r['rule_name'] for r in results['rule_results']]
        flag_rates = [r['flag_rate'] * 100 for r in results['rule_results']]
        flagged_counts = [r['flagged_count'] for r in results['rule_results']]
        
        if rule_names:
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.bar(
                    x=rule_names,
                    y=flag_rates,
                    title="Flag Rate by Rule (%)",
                    labels={'x': 'Rule', 'y': 'Flag Rate (%)'}
                )
                fig1.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(
                    x=rule_names,
                    y=flagged_counts,
                    title="Flagged Records by Rule",
                    labels={'x': 'Rule', 'y': 'Flagged Records'}
                )
                fig2.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig2, use_container_width=True)
        
        # Rule-specific results
        st.subheader("Rule Results")
        
        for rule_result in results['rule_results']:
            with st.expander(f"Rule: {rule_result['rule_name']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Flagged Rows", f"{rule_result['flagged_count']:,}")
                with col2:
                    st.metric("Flag Rate", f"{rule_result['flag_rate']:.2%}")
                with col3:
                    st.metric("Flagged Groups", rule_result.get('flagged_groups', 0))
                
                # Show sample flagged data
                if len(rule_result['flagged_data']) > 0:
                    st.write("**Sample Flagged Records:**")
                    display_df = rule_result['flagged_data'].head(10)
                    st.dataframe(display_df, use_container_width=True)
                    
                    if len(rule_result['flagged_data']) > 10:
                        st.write(f"... and {len(rule_result['flagged_data']) - 10} more flagged records")

def export_page():
    st.header("📥 Export Data")
    
    if st.session_state.uploaded_data is None:
        st.warning("Please upload data first!")
        return
    
    if st.session_state.analysis_results is None:
        st.warning("Please run analysis first!")
        return
    
    df = st.session_state.uploaded_data
    results = st.session_state.analysis_results
    export_manager = ExportManager()
    detector = FraudDetector()
    
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Excel with Highlights**")
        st.write("Original data with flagged rows highlighted in yellow")
        
        if st.button("Download Excel with Highlights", type="primary"):
            with st.spinner("Generating Excel file..."):
                excel_file = export_manager.create_excel_with_highlights(
                    df, 
                    results['combined_flagged_data'],
                    results
                )
                
                filename = export_manager.get_export_filename(
                    st.session_state.file_info['name'],
                    'highlighted',
                    'xlsx'
                )
                
                st.download_button(
                    label="📥 Download Highlighted Excel",
                    data=excel_file,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with col2:
        st.write("**✅ Clean Data Only**")
        st.write("Data with flagged rows removed")
        
        if st.button("Download Clean Data"):
            with st.spinner("Generating clean data..."):
                clean_data = detector.get_clean_data(df, results['combined_flagged_data'])
                
                # Excel format
                excel_file = export_manager.create_clean_excel(clean_data)
                filename_excel = export_manager.get_export_filename(
                    st.session_state.file_info['name'],
                    'clean',
                    'xlsx'
                )
                
                # CSV format
                csv_data = export_manager.create_csv_export(clean_data)
                filename_csv = export_manager.get_export_filename(
                    st.session_state.file_info['name'],
                    'clean',
                    'csv'
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        label="📥 Download Clean Excel",
                        data=excel_file,
                        file_name=filename_excel,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with col_b:
                    st.download_button(
                        label="📥 Download Clean CSV",
                        data=csv_data,
                        file_name=filename_csv,
                        mime="text/csv"
                    )
    
    # Export statistics
    st.subheader("Export Statistics")
    
    if results['combined_flagged_data'] is not None and len(results['combined_flagged_data']) > 0:
        clean_data = detector.get_clean_data(df, results['combined_flagged_data'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Original Rows", f"{len(df):,}")
        with col2:
            st.metric("Clean Rows", f"{len(clean_data):,}")
        with col3:
            st.metric("Removed Rows", f"{len(df) - len(clean_data):,}")

def generate_sample_data():
    """Generate sample data for testing."""
    np.random.seed(42)
    
    # Sample data with potential fraud patterns
    n_rows = 1000
    
    # Generate base data
    ic_numbers = [f"12345678{str(i).zfill(4)}" for i in range(1, 201)]
    bank_accounts = [f"ACC{str(i).zfill(8)}" for i in range(1, 151)]
    names = [f"Person {i}" for i in range(1, 301)]
    
    data = []
    
    for i in range(n_rows):
        # Most records are normal
        if i < 800:
            ic = np.random.choice(ic_numbers)
            bank = np.random.choice(bank_accounts)
            name = np.random.choice(names)
        else:
            # Introduce fraud patterns
            if i < 850:
                # Same IC, different bank accounts
                ic = ic_numbers[0]
                bank = np.random.choice(bank_accounts[:5])
                name = names[0]
            elif i < 900:
                # Same bank account, different ICs
                ic = np.random.choice(ic_numbers[:5])
                bank = bank_accounts[0]
                name = np.random.choice(names[:5])
            else:
                # Same bank account, different names
                ic = np.random.choice(ic_numbers[:3])
                bank = bank_accounts[1]
                name = np.random.choice(names[:3])
        
        data.append({
            'IC_Number': ic,
            'Bank_Account': bank,
            'Full_Name': name,
            'Amount': np.random.uniform(100, 10000),
            'Payment_Date': pd.date_range('2024-01-01', periods=30)[i % 30],
            'Department': np.random.choice(['Health', 'Education', 'Transport', 'Social'])
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    main()