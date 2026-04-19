from flask import Blueprint, send_file, Response
from services.db_service import db
from services.export_service import export_service
from config import Config
import io

report_bp = Blueprint('report', __name__)

@report_bp.route('/csv', methods=['GET'])
def export_csv():
    # All records
    detections = list(db.detections.find().sort("timestamp", -1))
    csv_data = export_service.generate_csv(detections)
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=smartsort_history.csv"}
    )

@report_bp.route('/pdf', methods=['GET'])
def export_pdf():
    # Compile current stats
    total = db.detections.count_documents({})
    top_users = list(db.users.find({}, {"_id": 0}).sort("green_coins", -1).limit(3))
    
    summary = {
        "total": total,
        "efficiency": 75, # Mock efficiency
        "co2": round(total * Config.CO2_PER_ITEM, 2),
        "top_users": top_users
    }
    
    pdf_bytes = export_service.generate_pdf(summary)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        download_name='smartsort_report.pdf',
        as_attachment=True
    )
