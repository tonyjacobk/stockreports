import os
from datetime import datetime
report="/tmp/telg.log"
def generate_morning_log_report():
    log_path = report
    
    # Get today's date in YYYY-MM-DD format
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(today_str) 
    # Dictionary to hold keyword mapping
    # Key: search term in log | Value: count
    keyword_counts = {
        'Report date': 0,
        'thematic': 0,
        'Others': 0,
        'compbrok': 0,
        'dirbrk': 0,
        'already present': 0,
        'onreport': 0,
        'sector': 0,
        'daily': 0,
        'sectres':0,
        'compres':0,
        'IPO':0,
        'strategy':0,
        'econ':0,
        'File too huge':0,
        'othcomp':0
    }

    if not os.path.exists(log_path):
        return f"<p>Error: {log_path} not found.</p>"

    # Process the file
    with open(log_path, 'r') as file:
        for line in file:
            # Only process lines that contain today's date
            if today_str in line:
                for word in keyword_counts.keys():
                  tword=word
                  if word not in["already present","Report date", 'File too huge'] :
                      tword="is of type "+word
                  if tword in line:
                        keyword_counts[word] += 1

    # Assigning to specific variables as requested
    total_report = keyword_counts['Report date']
    thematic     = keyword_counts['thematic']
    others       = keyword_counts['Others']
    compbrok     = keyword_counts['compbrok']
    compres      = keyword_counts['compres']
    dirbrk       = keyword_counts['dirbrk']
    duplicates   = keyword_counts['already present']
    onreport     = keyword_counts['onreport']
    sector       = keyword_counts['sector']
    sectres      = keyword_counts['sectres']
    strategy     = keyword_counts['strategy']
    daily        = keyword_counts['daily']
    ipo          = keyword_counts['IPO']
    othcomp      = keyword_counts['othcomp']
    econ         = keyword_counts['econ']
    huge         = keyword_counts['File too huge']
    useful       =thematic+others+compbrok+compres+onreport+sector+othcomp
    # Generate HTML Table
    html_table = f"""
    <h3>Morning Summary: {today_str}</h3>
    <table border="1" style="border-collapse: collapse; font-family: sans-serif;">
        <tr style="background-color: #4CAF50; color: white;">
            <th style="padding: 10px;">Category</th>
            <th style="padding: 10px;">Count</th>
        </tr>
        <tr><td style="padding: 8px;">Total Report Date</td><td>{total_report}</td></tr>
        <tr><td style="padding: 8px;">Thematic</td><td>{thematic}</td></tr>
        <tr><td style="padding: 8px;">Others</td><td>{others}</td></tr>
        <tr><td style="padding: 8px;">Compbrok</td><td>{compbrok}</td></tr>
        <tr><td style="padding: 8px;">Dirbrk</td><td>{dirbrk}</td></tr>
        <tr><td style="padding: 8px;">Already Present (Duplicates)</td><td>{duplicates}</td></tr>
        <tr><td style="padding: 8px;">On Report</td><td>{onreport}</td></tr>
        <tr><td style="padding: 8px;">Sector</td><td>{sector}</td></tr>
        <tr><td style="padding: 8px;">Daily</td><td>{daily}</td></tr>
        <tr><td style="padding: 8px;">Strategy</td><td>{strategy}</td></tr>
        <tr><td style="padding: 8px;">Sector Results</td><td>{sectres}</td></tr>
        <tr><td style="padding: 8px;">IPO</td><td>{ipo}</td></tr>
        <tr><td style="padding: 8px;">Economy</td><td>{econ}</td></tr>
        <tr><td style="padding: 8px;">Company Results</td><td>{compres}</td></tr>
        <tr><td style="padding: 8px;">Huge</td><td>{huge}</td></tr>
        <tr><td style="padding: 8px;">Useful Reports</td><td>{useful}</td></tr>
    </table>
    """
    return html_table



from datetime import date
import html

def get_analysis_report(log_file="/tmp/telg.log"):
    """
    Reads the telegram log file and returns:
    1) HTML table with all 'File too huge ..' lines
    2) HTML table with summary counts (sector, Analysis, toohuge)
    """

    today = date.today().strftime("%Y-%m-%d")

    sector = 0
    analysis = 0
    toohuge = 0
    duplicate=0
    comprep=0
    huge_lines = []
   
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if today not in line:
                continue

            if "Mail Adding to sector reports" in line:
                sector += 1

            if "Need further analysis" in line:
                analysis += 1
            if "present in DB with URL" in line:
                duplicate += 1
            if " Data to be inserted into DB" in line:
                comprep += 1
            if "File too huge .." in line:
                toohuge += 1
                huge_lines.append(line.strip())
    accounted=comprep+duplicate+analysis+sector
    # -------- Table 1: Huge lines --------
    huge_table = """
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>#</th>
            <th>Log Line</th>
        </tr>
    """

    for idx, line in enumerate(huge_lines, 1):
        huge_table += f"""
        <tr>
            <td>{idx}</td>
            <td>{html.escape(line)}</td>
        </tr>
        """

    huge_table += "</table>"

    # -------- Table 2: Summary --------
    summary_table = f"""
    <h3>Analysis Summary: </h3>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Category</th>
            <th>Count</th>
        </tr>
        <tr>
            <td>Sector</td>
            <td>{sector}</td>
        </tr>
        <tr>
            <td>Analysis</td>
            <td>{analysis}</td>
        </tr>
        <tr>
            <td>Duplicate Company Report</td>
            <td>{duplicate}</td>
        </tr>
        <tr>
            <td>New Company Report</td>
            <td>{comprep}</td>
        </tr>
        <tr>
            <td>Reports Accounted </td>
            <td>{accounted}</td>
        </tr>

    </table>
    """

    return huge_table, summary_table

def get_all_tables():
    huge,summary=get_analysis_report(report)
    morning=generate_morning_log_report()
    return huge,summary,morning

if __name__ == "__main__":
    h,s,m=get_all_tables()
    print(h)
    print(s)
    print(m)

