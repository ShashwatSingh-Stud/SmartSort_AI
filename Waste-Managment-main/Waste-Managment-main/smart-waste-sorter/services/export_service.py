import csv
import io
from fpdf import FPDF
from datetime import datetime

class ExportService:
    @staticmethod
    def generate_csv(detections):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "Type", "Confidence", "Bin", "Zone", "Contaminated"])
        
        for d in detections:
            writer.writerow([
                d.get("timestamp"),
                d.get("waste_type"),
                d.get("confidence_score"),
                d.get("bin_id"),
                d.get("location_zone"),
                d.get("is_contamination")
            ])
        
        return output.getvalue()

    @staticmethod
    def generate_pdf(summary_data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "SmartSort AI — Waste Intelligence Report", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
        pdf.ln(10)

        # Session Stats
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Performance Summary (24H)", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, f"Total Items: {summary_data.get('total')}", ln=True)
        pdf.cell(0, 8, f"Recycling Efficiency: {summary_data.get('efficiency')}%", ln=True)
        pdf.cell(0, 8, f"CO2 Offset: {summary_data.get('co2')} KG", ln=True)
        pdf.ln(10)

        # Leaderboard
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Top Sustainability Champions", ln=True)
        pdf.set_font("Arial", size=11)
        for user in summary_data.get("top_users", []):
            pdf.cell(0, 8, f"• {user['user_name']} ({user['organization']}): {user['green_coins']} GreenCoins", ln=True)

        return pdf.output(dest='S').encode('latin-1')

export_service = ExportService()
