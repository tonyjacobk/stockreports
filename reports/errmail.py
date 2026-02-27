def find_error_context(file_path, target_word="error"):
    context_lines = []
    skip_above_patterns = [
        "INFO - IBS Report date from first row start_date",
        "INFO - IMail: BS Searching for reports newer than"
    ]
    skip_error_pattern = "Error parsing below HTML row: 'NoneType' object has no attribute 'find'"

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    target_word_lower = target_word.lower()
    for i, line in enumerate(lines):
        if target_word_lower in line.lower():
            current = line.strip()
            above = lines[i - 1].strip() if i > 0 else " "
            below = lines[i + 1].strip() if i + 1 < len(lines) else " "

            # Skip if error line matches and above line matches any skip pattern
            if (
                skip_error_pattern in current
                and above
                and any(pattern in above for pattern in skip_above_patterns)
            ):
                continue

            context_lines.append((above, current, below))
    return context_lines
def create_error_report():
     file_path = '/tmp/myapp.log'
     c=find_error_context(file_path)
     rep=""+"Following error messages were found"+"\n"
     for x,y,z in c:
      rep=rep+x+"\n"
      rep=rep+y+"\n"
      rep=rep+z+"\n"
      rep=rep+"********************************************************************************************"+"\n"
     return(rep) 
c=create_error_report()
print(c)
