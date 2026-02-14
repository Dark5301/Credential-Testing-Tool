class InputEngine:
    def __init__(self, filepath, delimiter=None):
        self.filepath = filepath
        self.delimiter = delimiter

    def load_credentials(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    clean_line = line.strip()

                    # CHECK 1: Is the line empty?
                    if clean_line == "":
                        continue

                    # If user specified a delimiter, use only that one
                    if self.delimiter:
                        delimiters = [self.delimiter]
                    else:          # Otherwise, try common delimiters
                        delimiters = [':', ',', ';', '|']

                    parts = None

                    for delimiter in delimiters:
                        if delimiter in clean_line:
                            parts = clean_line.split(delimiter, 1)
                            break # Stop after finding the first valid delimiter

                    # CHECK 2: Did we find a delimiter and get 2 parts?
                    if parts is None or len(parts) != 2:
                        continue

                    username = parts[0].strip()
                    password = parts[1].strip()

                    # CHECK 3: Are username and password non-empty?
                    if username == "" or password == "":
                        continue

                    yield (username, password)
        except FileNotFoundError:
            print(f"Error: File '{self.filepath}' not found.")
            return
