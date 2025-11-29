with open('status_result.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if "DEBUG ERROR" in line:
            print(line.strip())
        if "LINGO STATUS" in line:
            print(line.strip())
        if "MODE:" in line:
            print(line.strip())
