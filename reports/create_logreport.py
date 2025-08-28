import re
from datetime import datetime

def parse_log_file(log_file):
    log_lines=open(log_file,"r")
    shareindia_data = {
        'Long Term Stock': 0,
        'Short Term Stock': 0,
        'Thematic Stocks': 0,
        'Special Reports': 0
    }
    
    smifs_data = {
        'Initiating Coverage': 0,
        'Pick of Month': 0,
        'Results': 0
    }
    
    source_data = []
    code_db_added = []  # For "Added to Code DB" entries
    code_db_failed = []  # For "Could not add to code DB" entries
    check_date = None
    
    for line in log_lines:
        # Extract the check date from any source line
        if 'Searching for reports newer than' in line and not check_date:
            match = re.search(r'newer than (.*\d{4} \d{2}:\d{2} [AP]M \w+)', line)
            if match:
                check_date = match.group(1)
        
        # ShareIndia parsing
        if 'Shareindia After tab-content-long-term-stock' in line:
            match = re.search(r'total new reports (\d+)', line)
            if match:
                shareindia_data['Long Term Stock'] = int(match.group(1))
        
        elif 'Shareindia After tab-content-short-term-stock' in line:
            match = re.search(r'total new reports (\d+)', line)
            if match:
                shareindia_data['Short Term Stock'] = int(match.group(1))
        
        elif 'Shareindia After tab-content-thematic-stocks' in line:
            match = re.search(r'total new reports (\d+)', line)
            if match:
                shareindia_data['Thematic Stocks'] = int(match.group(1))
        
        elif 'Shareindia After tab-content-special-reports' in line:
            match = re.search(r'total new reports (\d+)', line)
            if match:
                shareindia_data['Special Reports'] = int(match.group(1))
        
        # SMIFS parsing
        elif 'SMIFS Found' in line:
            if 'Initiating Coverage' in line:
                match = re.search(r'Found (\d+) new reports', line)
                if match:
                    smifs_data['Initiating Coverage'] = int(match.group(1))
            
            elif 'Pick of Month' in line:
                match = re.search(r'Found (\d+) new reports', line)
                if match:
                    smifs_data['Pick of Month'] = int(match.group(1))
            
            elif 'Results' in line:
                match = re.search(r'Found (\d+) new reports', line)
                if match:
                    smifs_data['Results'] = int(match.group(1))
        
        # Source data parsing (MC, BS, etc.)
        elif re.match(r'.*Mail: (MC|BS|Axis|Geojith|IDBI)', line):
            source_match = re.search(r'Mail: (\w+)', line)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            found_match = re.search(r'Found (\d+) new reports', line)
            added_match = re.search(r'Found (\d+) reports for adding to db', line)
            
            if source_match:
                source = source_match.group(1)
                date = date_match.group(1) if date_match else ''
                found = found_match.group(1) if found_match else '0'
                added = added_match.group(1) if added_match else '0'
                
                # Check if we already have an entry for this source and date
                existing_entry = next((item for item in source_data if item['source'] == source and item['date'] == date), None)
                
                if existing_entry:
                    if found_match:
                        existing_entry['found'] = found
                    if added_match:
                        existing_entry['added'] = added
                else:
                    source_data.append({
                        'source': source,
                        'date': date,
                        'found': found,
                        'added': added
                    })
        
        # Added to Code DB parsing
        elif 'Mail:Added to codeDB' in line:
            # Extract company name and code
            match = re.search(r'Mail:Added to codeDB (.+)', line)
            if match:
                full_text = match.group(1).strip()
                # Split by space and get last word as code
                parts = full_text.split()
                if len(parts) >= 2:
                    code = parts[-1]
                    company_name = ' '.join(parts[:-1])
                    code_db_added.append({
                        'name': company_name,
                        'code': code
                    })
        
        # Could not add to code DB parsing
        elif 'Mail:Could not find NSECode for' in line:
            match = re.search(r'Mail:Could not find NSECode for (.+)', line)
            if match:
                company_name = match.group(1).strip()
                code_db_failed.append({
                    'name': company_name,
                    'code': 'N/A'
                })
    
    return shareindia_data, smifs_data, source_data, code_db_added, code_db_failed, check_date

def generate_html_tables(shareindia_data, smifs_data, source_data, code_db_added, code_db_failed, check_date):
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Report Summary (since {check_date})</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        h1, h2 {{
            color: #333;
        }}
        table {{
            border-collapse: collapse;
            width: 80%;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .timestamp {{
            font-size: 0.8em;
            color: #666;
            margin-bottom: 20px;
        }}
        .check-date {{
            font-size: 1em;
            color: #444;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        .source-table {{
            width: 100%;
        }}
        .code-table {{
            width: 60%;
        }}
    </style>
</head>
<body>
    <h1>Report Summary</h1>
    <div class="timestamp">Generated on: {current_date}</div>
    <div class="check-date">Showing reports newer than: {check_date}</div>
    
    <h2>Source Reports</h2>
    <table class="source-table">
        <tr>
            <th>Source</th>
            <th>Date</th>
            <th>Found</th>
            <th>Added to DB</th>
        </tr>
"""
    
    # Add Source table rows
    for entry in source_data:
        html += f"""
        <tr>
            <td>{entry['source']}</td>
            <td>{entry['date']}</td>
            <td>{entry['found']}</td>
            <td>{entry['added']}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>Added to Code DB</h2>
    <table class="code-table">
        <tr>
            <th>Name</th>
            <th>Code</th>
        </tr>
"""
    
    # Add Code DB Added table rows
    for entry in code_db_added:
        html += f"""
        <tr>
            <td>{entry['name']}</td>
            <td>{entry['code']}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>Could not add to code DB</h2>
    <table class="code-table">
        <tr>
            <th>Name</th>
            <th>Code</th>
        </tr>
"""
    
    # Add Code DB Failed table rows
    for entry in code_db_failed:
        html += f"""
        <tr>
            <td>{entry['name']}</td>
            <td>{entry['code']}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>ShareIndia Reports</h2>
    <table>
        <tr>
            <th>Report Type</th>
            <th>Number of Reports</th>
        </tr>
"""
    
    # Add ShareIndia table rows
    for report_type, count in shareindia_data.items():
        html += f"""
        <tr>
            <td>{report_type}</td>
            <td>{count}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>SMIFS Reports</h2>
    <table>
        <tr>
            <th>Report Type</th>
            <th>Number of Reports</th>
        </tr>
"""
    
    # Add SMIFS table rows
    for report_type, count in smifs_data.items():
        html += f"""
        <tr>
            <td>{report_type}</td>
            <td>{count}</td>
        </tr>
"""
    
    html += """
    </table>
</body>
</html>
"""
    
    return html

# Example usage with the log lines including MC data and code DB entries
def get_report():
 shareindia_data, smifs_data, source_data, code_db_added, code_db_failed, check_date = parse_log_file("/tmp/maillog")
 html_output = generate_html_tables(shareindia_data, smifs_data, source_data, code_db_added, code_db_failed, check_date)
 return(html_output)
