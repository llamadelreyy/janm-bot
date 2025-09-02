from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import json
import io
from datetime import datetime

# Import our custom modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.file_processor import FileProcessor
from src.rule_engine import RuleEngine
from src.fraud_detector import FraudDetector
from src.export_manager import ExportManager

app = FastAPI(title="Fraud Detection API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage (in production, use a proper database)
app_state = {
    "uploaded_data": None,
    "file_info": None,
    "rules": [],
    "analysis_results": None
}

# Pydantic models
class Rule(BaseModel):
    name: str
    group_by: str
    compare: str
    comparison_parameter: str = "same_group_different_values"

class RuleUpdate(BaseModel):
    rules: List[Dict[str, Any]]

class AnalysisRequest(BaseModel):
    rules: List[Dict[str, Any]]

@app.get("/")
async def root():
    return {"message": "Fraud Detection API is running"}

@app.get("/status")
async def get_status():
    """Get current application status"""
    return {
        "data_uploaded": app_state["uploaded_data"] is not None,
        "data_rows": len(app_state["uploaded_data"]) if app_state["uploaded_data"] is not None else 0,
        "rules_count": len(app_state["rules"]),
        "analysis_completed": app_state["analysis_results"] is not None,
        "file_info": app_state["file_info"]
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process Excel/CSV file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Process file
        processor = FileProcessor()
        
        # Create a file-like object from the uploaded file
        file_content = await file.read()
        file_obj = io.BytesIO(file_content)
        file_obj.name = file.filename
        file_obj.size = len(file_content)
        
        df, file_info = processor.process_file(file_obj)
        
        # Store in app state
        app_state["uploaded_data"] = df
        app_state["file_info"] = file_info
        app_state["analysis_results"] = None  # Clear previous analysis
        
        # Clean data for JSON serialization
        preview_df = df.head(10).fillna('')  # Replace NaN with empty string
        
        # Return file info and preview
        return {
            "success": True,
            "file_info": file_info,
            "columns": df.columns.tolist(),
            "preview": preview_df.to_dict('records'),
            "data_quality": {
                "missing_values": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.astype(str).to_dict()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/columns")
async def get_columns():
    """Get available columns from uploaded data"""
    if app_state["uploaded_data"] is None:
        raise HTTPException(status_code=400, detail="No data uploaded")
    
    return {
        "columns": app_state["uploaded_data"].columns.tolist()
    }

@app.get("/rule-suggestions")
async def get_rule_suggestions():
    """Get suggested rules based on column names"""
    if app_state["uploaded_data"] is None:
        raise HTTPException(status_code=400, detail="No data uploaded")
    
    rule_engine = RuleEngine()
    columns = app_state["uploaded_data"].columns.tolist()
    suggestions = rule_engine.get_rule_suggestions(columns)
    
    return {
        "suggestions": suggestions,
        "comparison_parameters": rule_engine.get_comparison_parameters()
    }

@app.post("/rules")
async def create_rule(rule: Rule):
    """Create a new fraud detection rule"""
    if app_state["uploaded_data"] is None:
        raise HTTPException(status_code=400, detail="No data uploaded")
    
    try:
        rule_engine = RuleEngine()
        columns = app_state["uploaded_data"].columns.tolist()
        
        # Validate rule
        rule_dict = rule.dict()
        validation = rule_engine.validate_rule(rule_dict, columns)
        
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["errors"])
        
        # Create rule
        new_rule = rule_engine.create_rule(
            rule.name,
            rule.group_by,
            rule.compare,
            rule.comparison_parameter
        )
        
        app_state["rules"].append(new_rule)
        
        return {
            "success": True,
            "rule": new_rule,
            "total_rules": len(app_state["rules"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/rules")
async def get_rules():
    """Get all configured rules"""
    return {
        "rules": app_state["rules"]
    }

@app.delete("/rules/{rule_index}")
async def delete_rule(rule_index: int):
    """Delete a rule by index"""
    if rule_index < 0 or rule_index >= len(app_state["rules"]):
        raise HTTPException(status_code=404, detail="Rule not found")
    
    removed_rule = app_state["rules"].pop(rule_index)
    
    return {
        "success": True,
        "removed_rule": removed_rule,
        "total_rules": len(app_state["rules"])
    }

@app.post("/rules/{rule_index}/preview")
async def preview_rule(rule_index: int):
    """Preview a specific rule"""
    if app_state["uploaded_data"] is None:
        raise HTTPException(status_code=400, detail="No data uploaded")
    
    if rule_index < 0 or rule_index >= len(app_state["rules"]):
        raise HTTPException(status_code=404, detail="Rule not found")
    
    try:
        detector = FraudDetector()
        rule = app_state["rules"][rule_index]
        preview_results = detector.preview_rule(app_state["uploaded_data"], rule)
        
        return {
            "success": True,
            "preview": preview_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze")
async def run_analysis():
    """Run fraud analysis on all configured rules"""
    if app_state["uploaded_data"] is None:
        raise HTTPException(status_code=400, detail="No data uploaded")
    
    if not app_state["rules"]:
        raise HTTPException(status_code=400, detail="No rules configured")
    
    try:
        detector = FraudDetector()
        results = detector.analyze_all_rules(app_state["uploaded_data"], app_state["rules"])
        
        # Store results
        app_state["analysis_results"] = results
        
        # Convert DataFrames to serializable format
        serializable_results = {
            "total_flagged": results["total_flagged"],
            "overall_flag_rate": results["overall_flag_rate"],
            "total_rows": results["total_rows"],
            "rules_count": results["rules_count"],
            "success": results["success"],
            "rule_results": []
        }
        
        for rule_result in results["rule_results"]:
            serializable_rule_result = {
                "rule_name": rule_result["rule_name"],
                "flagged_count": rule_result["flagged_count"],
                "flag_rate": rule_result["flag_rate"],
                "flagged_groups": rule_result.get("flagged_groups", 0),
                "total_groups": rule_result.get("total_groups", 0),
                "success": rule_result["success"],
                "flagged_data_preview": rule_result["flagged_data"].head(10).fillna('').to_dict('records') if len(rule_result["flagged_data"]) > 0 else []
            }
            serializable_results["rule_results"].append(serializable_rule_result)
        
        return serializable_results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analysis/results")
async def get_analysis_results():
    """Get the latest analysis results"""
    if app_state["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="No analysis results available")
    
    results = app_state["analysis_results"]
    
    # Convert to serializable format
    serializable_results = {
        "total_flagged": results["total_flagged"],
        "overall_flag_rate": results["overall_flag_rate"],
        "total_rows": results["total_rows"],
        "rules_count": results["rules_count"],
        "success": results["success"],
        "rule_results": []
    }
    
    for rule_result in results["rule_results"]:
        serializable_rule_result = {
            "rule_name": rule_result["rule_name"],
            "flagged_count": rule_result["flagged_count"],
            "flag_rate": rule_result["flag_rate"],
            "flagged_groups": rule_result.get("flagged_groups", 0),
            "total_groups": rule_result.get("total_groups", 0),
            "success": rule_result["success"],
            "flagged_data_preview": rule_result["flagged_data"].head(10).fillna('').to_dict('records') if len(rule_result["flagged_data"]) > 0 else []
        }
        serializable_results["rule_results"].append(serializable_rule_result)
    
    return serializable_results

@app.get("/export/highlighted")
async def export_highlighted():
    """Export data with highlighted flagged rows"""
    if app_state["uploaded_data"] is None or app_state["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="No data or analysis results available")
    
    try:
        export_manager = ExportManager()
        excel_file = export_manager.create_excel_with_highlights(
            app_state["uploaded_data"],
            app_state["analysis_results"]["combined_flagged_data"],
            app_state["analysis_results"]
        )
        
        filename = export_manager.get_export_filename(
            app_state["file_info"]["name"],
            "highlighted",
            "xlsx"
        )
        
        return StreamingResponse(
            io.BytesIO(excel_file.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/export/clean")
async def export_clean():
    """Export clean data (flagged rows removed)"""
    if app_state["uploaded_data"] is None or app_state["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="No data or analysis results available")
    
    try:
        detector = FraudDetector()
        clean_data = detector.get_clean_data(
            app_state["uploaded_data"],
            app_state["analysis_results"]["combined_flagged_data"]
        )
        
        export_manager = ExportManager()
        excel_file = export_manager.create_clean_excel(clean_data)
        
        filename = export_manager.get_export_filename(
            app_state["file_info"]["name"],
            "clean",
            "xlsx"
        )
        
        return StreamingResponse(
            io.BytesIO(excel_file.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/export/clean-csv")
async def export_clean_csv():
    """Export clean data as CSV"""
    if app_state["uploaded_data"] is None or app_state["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="No data or analysis results available")
    
    try:
        detector = FraudDetector()
        clean_data = detector.get_clean_data(
            app_state["uploaded_data"],
            app_state["analysis_results"]["combined_flagged_data"]
        )
        
        export_manager = ExportManager()
        csv_data = export_manager.create_csv_export(clean_data)
        
        filename = export_manager.get_export_filename(
            app_state["file_info"]["name"],
            "clean",
            "csv"
        )
        
        return StreamingResponse(
            io.StringIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sample-data")
async def generate_sample_data():
    """Generate sample data for testing"""
    try:
        # Import the sample data generation function
        import numpy as np
        
        # Generate sample data (copied from app.py)
        np.random.seed(42)
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
        
        sample_df = pd.DataFrame(data)
        
        # Store in app state
        app_state["uploaded_data"] = sample_df
        app_state["file_info"] = {
            'name': 'sample_data.csv',
            'size': '15.2 KB',
            'rows': len(sample_df),
            'columns': len(sample_df.columns),
            'extension': '.csv'
        }
        app_state["analysis_results"] = None
        
        # Clean data for JSON serialization
        preview_df = sample_df.head(10).fillna('')  # Replace NaN with empty string
        
        return {
            "success": True,
            "file_info": app_state["file_info"],
            "columns": sample_df.columns.tolist(),
            "preview": preview_df.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)