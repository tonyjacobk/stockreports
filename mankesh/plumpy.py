import pdfplumber

with pdfplumber.open("tempfile") as pdf:
    # Iterate through each page
    for page in pdf.pages:
        # Extract plain text
        text = page.extract_text()
        print(text)
        
        # Extract tables
        tables = page.extract_tables()
        for table in tables:
            print(table)
