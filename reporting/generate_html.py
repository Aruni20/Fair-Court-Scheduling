# reporting/generate_html.py
"""
Generate professional HTML reports for daily court schedules and upload to web server.
Fetches case details from MySQL for formal presentation.
"""

from jinja2 import Template
import os
import mysql.connector
import shutil
from datetime import datetime
from config.config import MYSQL_CONN

def fetch_schedule_details(schedules):
    """Fetch detailed schedule information from MySQL."""
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="court_db"
        )
        cursor = conn.cursor(dictionary=True)
        
        enriched_schedules = []
        for schedule in schedules:
            # Fetch case details
            cursor.execute("""
                SELECT c.case_number, ct.type_name
                FROM Case c
                JOIN Case_Type ct ON c.case_type_id = ct.case_type_id
                WHERE c.case_id = %s
            """, (schedule['case_id'],))
            case_info = cursor.fetchone()
            
            # Fetch court and judge details
            cursor.execute("""
                SELECT j.full_name AS judge_name, c.court_name
                FROM Judge j
                JOIN Court c ON c.court_id = %s
                WHERE j.judge_id = %s
            """, (schedule['court_id'], schedule['judge_id']))
            court_judge_info = cursor.fetchone()
            
            enriched_schedules.append({
                'case_number': case_info['case_number'] if case_info else schedule['case_id'],
                'case_type': case_info['type_name'] if case_info else 'Unknown',
                'court_name': court_judge_info['court_name'] if court_judge_info else schedule['court_id'],
                'judge_name': court_judge_info['judge_name'] if court_judge_info else schedule['judge_id'],
                'scheduled_date': schedule['scheduled_date'],
                'start_time': schedule['start_time'],
                'end_time': schedule['end_time']
            })
        
        cursor.close()
        conn.close()
        return enriched_schedules
    except Exception as e:
        print(f"Error fetching schedule details: {e}")
        raise

def generate_schedule_html(schedules, output_path):
    """Generate professional HTML report from schedules."""
    try:
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Court Schedule - {{ date }}</title>
            <style>
                body {
                    font-family: 'Times New Roman', Times, serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f9;
                    color: #333;
                }
                .container {
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: #fff;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                .header {
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 2px solid #003087;
                }
                .header img {
                    max-width: 100px;
                    vertical-align: middle;
                }
                .header h1 {
                    margin: 10px 0;
                    font-size: 28px;
                    color: #003087;
                    font-weight: bold;
                }
                .header p {
                    margin: 5px 0;
                    font-size: 16px;
                    color: #555;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                }
                th {
                    background-color: #003087;
                    color: white;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                tr:hover {
                    background-color: #e6f0fa;
                }
                .footer {
                    text-align: center;
                    padding: 10px 0;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #ddd;
                    margin-top: 20px;
                }
                .footer p {
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="/static/court_logo.png" alt="Court Emblem">
                    <h1>Daily Court Schedule - {{ date }}</h1>
                    <p>Supreme Court of India - e-Court System</p>
                    <p>Generated on {{ date }} at 23:00 IST</p>
                </div>
                <table>
                    <tr>
                        <th>Case Number</th>
                        <th>Case Type</th>
                        <th>Court</th>
                        <th>Judge</th>
                        <th>Date</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                    </tr>
                    {% for schedule in schedules %}
                    <tr>
                        <td>{{ schedule.case_number }}</td>
                        <td>{{ schedule.case_type }}</td>
                        <td>{{ schedule.court_name }}</td>
                        <td>{{ schedule.judge_name }}</td>
                        <td>{{ schedule.scheduled_date }}</td>
                        <td>{{ schedule.start_time }}</td>
                        <td>{{ schedule.end_time }}</td>
                    </tr>
                    {% endfor %}
                </table>
                <div class="footer">
                    <p>Contact: registrar@supremecourt.gov.in | Phone: +91-11-2311-1400</p>
                    <p>Confidential: For authorized personnel only. Unauthorized distribution prohibited.</p>
                    <p>Supreme Court of India, New Delhi</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Enrich schedules with case, court, and judge details
        enriched_schedules = fetch_schedule_details(schedules)
        
        # Generate HTML
        template = Template(template_str)
        date_str = datetime.now().strftime("%Y-%m-%d")
        html_content = template.render(schedules=enriched_schedules, date=date_str)
        
        # Save HTML to output path
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"Generated HTML report at {output_path}")
        return html_content, date_str
    except Exception as e:
        print(f"Error generating HTML: {e}")
        raise

def upload_to_web_server(html_path, date_str):
    """Upload HTML report to web server directory."""
    try:
        web_dir = "/var/www/html/schedules"
        os.makedirs(web_dir, exist_ok=True)
        dest_path = os.path.join(web_dir, f"schedule_{date_str}.html")
        shutil.copy(html_path, dest_path)
        print(f"Uploaded HTML report to {dest_path}")
        return f"http://localhost:8080/schedules/schedule_{date_str}.html"
    except Exception as e:
        print(f"Error uploading to web server: {e}")
        raise