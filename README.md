# Credential Testing Tool

A professional-grade, multi-threaded credential validation system built in Python. This tool uses differential analysis to intelligently detect successful login attempts by comparing responses against a learned failure pattern.

---

## 🎯 **Project Overview**

This credential testing tool was built to demonstrate modern techniques used in security testing and penetration testing. It implements a sophisticated detection system that doesn't rely on simple keyword matching, but instead learns what "failure" looks like and detects anomalies.

### **Key Features**

- ✅ **Intelligent Detection**: Uses differential analysis instead of simple pattern matching
- ✅ **Memory Efficient**: Processes credentials via generators (handles 100,000+ credentials)
- ✅ **Multi-threaded**: Concurrent testing with configurable worker threads
- ✅ **Browser Mimicry**: Realistic headers to avoid bot detection
- ✅ **Flexible Input**: Handles messy credential files with multiple delimiters
- ✅ **Auto-calibration**: Learns failure patterns automatically
- ✅ **Interactive Mode**: User-friendly CLI interface
- ✅ **Result Logging**: Automatic saving of valid credentials

---

## 📋 **Table of Contents**

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [Legal Disclaimer](#legal-disclaimer)
- [Contributing](#contributing)
- [License](#license)

---

## 🔬 **How It Works**

### **The Differential Analysis Approach**

Unlike traditional credential stuffing tools that look for success keywords, this tool uses a more sophisticated approach:

1. **Calibration Phase**: Sends 5 fake login attempts with obviously invalid credentials
2. **Pattern Analysis**: Identifies what's *consistent* across all failures (status codes, response lengths, redirects)
3. **Detection Phase**: Tests real credentials and flags any response that *deviates* from the failure pattern
4. **Scoring System**: Uses a point-based system (0-8 points) to determine confidence level

**Why This Works:**
- ✅ No need to know what success looks like
- ✅ Adapts automatically to any website
- ✅ Detects subtle differences (redirects, cookies, response size changes)
- ✅ More reliable than keyword matching

---

## 🏗️ **Architecture**

### **System Components**

```
┌─────────────────────────────────────────────────────────┐
│                    CREDENTIAL TESTER                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Phase 1: INPUT ENGINE                                  │
│  ├─ Reads combo.txt                                     │
│  ├─ Handles multiple delimiters (: ; | ,)              │
│  ├─ Validates and sanitizes data                       │
│  └─ Yields credentials one at a time (generator)       │
│                                                          │
│  Phase 2: REQUEST ARCHITECT                             │
│  ├─ Creates realistic browser session                  │
│  ├─ Sets Chrome-like headers                           │
│  ├─ Manages cookies automatically                      │
│  └─ Sends POST requests                                │
│                                                          │
│  Phase 3: THREADING LAYER                               │
│  ├─ Queue-based task distribution                      │
│  ├─ Configurable worker threads (3-20)                 │
│  ├─ Thread-safe operations                             │
│  └─ Rate limiting controls                             │
│                                                          │
│  Phase 4: LOGIN DETECTOR                                │
│  ├─ Calibrator: Learns failure patterns                │
│  ├─ PatternAnalyzer: Identifies consistency            │
│  ├─ LoginDetector: Scores deviations                   │
│  └─ Decision engine (threshold: 3/8 points)           │
│                                                          │
│  Phase 5: RESULT LOGGER                                 │
│  ├─ Saves valid credentials immediately                │
│  ├─ Timestamps all results                             │
│  └─ Thread-safe file operations                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### **File Structure**

```
credential-testing-tool/
├── input_engine.py          # Phase 1: Credential file parser
├── request_architect.py     # Phase 2: HTTP session manager
├── login_detector.py        # Phase 4: Detection system
│   ├── Calibrator          # Learns failure patterns
│   ├── PatternAnalyzer     # Analyzes consistency
│   └── LoginDetector       # Scores responses
├── credential_checker.py    # Single-threaded implementation
├── threaded_checker.py      # Multi-threaded implementation
├── easy_checker.py          # Interactive CLI version
├── combo.txt                # Input credentials file
├── valid_accounts.txt       # Output results (auto-generated)
└── README.md                # This file
```

---

## 💾 **Installation**

### **Prerequisites**

- Python 3.7 or higher
- pip (Python package manager)

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/Dark5301/credential-testing-tool.git
cd credential-testing-tool
```

### **Step 2: Install Dependencies**

```bash
pip install requests
```

### **Step 3: Prepare Your Credential File**

Create a `combo.txt` file with credentials (one per line):

```
username1:password1
user2@email.com:pass123
alice;password456
bob|secret789
```

**Supported delimiters**: `:` `;` `|` `,`

---

## 🚀 **Usage**

### **Option 1: Interactive Mode (Recommended for Beginners)**

```bash
python easy_checker.py
```

The tool will prompt you for:
- Combo file path
- Login URL endpoint
- Form field names (username/password)
- Number of threads

**Example Session:**
```
Enter path to combo file (default: combo.txt): 
Enter login URL: https://example.com/login
Enter username field name (default: username): email
Enter password field name (default: password): 
Enter number of threads (default: 5): 3

Proceed? (yes/no): yes
```

### **Option 2: Programmatic Mode (For Advanced Users)**

Edit `threaded_checker.py` configuration:

```python
def main():
    combo_file = 'combo.txt'
    login_url = 'https://example.com/login'
    username_field = 'email'
    password_field = 'password'
    num_threads = 5
```

Then run:
```bash
python threaded_checker.py
```

### **Option 3: Single-Threaded (For Testing)**

```bash
python credential_checker.py
```

Useful for:
- Testing against slow servers
- Debugging detection logic
- Avoiding rate limits

---

## ⚙️ **Configuration**

### **Finding the Login Endpoint**

1. **Open Chrome DevTools** (F12)
2. **Go to Network tab**
3. **Attempt login** with fake credentials
4. **Look for POST request** (usually red/pink)
5. **Copy the Request URL** (e.g., `https://example.com/session`)

### **Finding Form Field Names**

1. **Right-click on username field** → Inspect Element
2. **Look for `<input name="...">` attribute**

**Example:**
```html
<input name="email" type="text" />
<input name="password" type="password" />
```
→ Use `username_field='email'` and `password_field='password'`

### **Threading Guidelines**

| Scenario | Threads | Delay | Speed |
|----------|---------|-------|-------|
| Testing/Learning | 3-5 | 2s | ~2 creds/sec |
| Production (careful) | 5-10 | 2s | ~5 creds/sec |
| Aggressive (risk ban) | 10-20 | 1s | ~15 creds/sec |

**⚠️ Warning**: Higher threads = faster but more likely to trigger rate limiting!

---

## 📖 **Examples**

### **Example 1: Testing on Practice Site**

```bash
python easy_checker.py
```

```
Enter login URL: http://testphp.vulnweb.com/login.php
Enter username field name: uname
Enter password field name: pass
Enter number of threads: 3
```

### **Example 2: GitHub (Educational)**

```bash
python threaded_checker.py
```

**Configuration:**
```python
login_url = 'https://github.com/session'
username_field = 'login'  # GitHub uses 'login' not 'username'!
password_field = 'password'
num_threads = 3  # Low to avoid IP ban
```

**⚠️ Note**: GitHub has aggressive rate limiting. Use with extreme caution.

### **Example 3: Custom Form Fields**

For a site with custom field names:

```html
<input name="user_email" type="text" />
<input name="user_pwd" type="password" />
```

**Configuration:**
```python
username_field = 'user_email'
password_field = 'user_pwd'
```

---

## 🔍 **Understanding the Output**

### **Calibration Phase**

```
============================================================
CALIBRATION PHASE: Establishing failure pattern
============================================================
Calibration 1/5:
  Status: 422
  Length: 9309 bytes
  URL: https://example.com/login
```

**What it means**: The tool is learning what failed logins look like.

### **Pattern Analysis**

```
============================================================
PATTERN ANALYSIS: Finding failure signature
============================================================
Status codes: [422, 422, 422, 422, 422]
Response lengths: [9309, 9309, 9309, 9309, 9309]

✓ Failure Pattern Identified:
  Expected Status: 422
  Expected Length Range: 9259-9359 bytes
  Expected URL: https://example.com/login
```

**What it means**: All failures are consistent - this is the "fingerprint" of failure.

### **Testing Phase**

```
============================================================
TESTING IN PROGRESS...
============================================================
   ❌ 1. user1:pass1
   ❌ 2. user2:pass2
   
🎯 [Thread-2] POTENTIAL HIT: admin:password123
   Deviation Score: 5/8
   - Status changed: 422 → 302
   - Redirected: /login → /dashboard
```

**What it means**: 
- `❌` = Response matched failure pattern (invalid credentials)
- `🎯` = Response deviated from pattern (potential valid login!)

### **Deviation Scoring**

| Points | Indicator |
|--------|-----------|
| +3 | Status code changed (e.g., 422 → 302) |
| +2 | Response length anomaly (significantly different) |
| +3 | URL changed (redirect detected) |

**Decision threshold**: ≥3 points = Likely success

---

## 🎓 **Technical Deep Dive**

### **Why Differential Analysis?**

Traditional methods fail because:
- ❌ Keywords change ("Invalid password" vs "Incorrect credentials")
- ❌ Success pages vary wildly across sites
- ❌ Some sites return 200 OK even for failures

Differential analysis succeeds because:
- ✅ Learns the site's specific failure behavior
- ✅ Detects *any* deviation from the norm
- ✅ Adapts automatically to each target

### **Memory Efficiency**

**Problem**: Loading 100,000 credentials into memory → ~10-50 MB RAM

**Solution**: Python generators
```python
def load_credentials(self):
    for line in file:
        yield (username, password)  # Yields one at a time
```

**Result**: Constant memory usage regardless of file size!

### **Thread Safety**

**Problem**: Multiple threads writing to the same file = data corruption

**Solution**: Thread locks
```python
with self.lock:
    self.tested_count += 1
    self.save_valid_credential(username, password)
```

**Result**: Safe concurrent operations!

---

## ⚠️ **Legal Disclaimer**

### **IMPORTANT: READ BEFORE USE**

This tool is provided for **educational and authorized security testing purposes only**.

### **Legal Use Cases:**
✅ Testing your own applications  
✅ Authorized penetration testing with written permission  
✅ Security research in controlled lab environments  
✅ Educational demonstrations on practice sites  

### **Illegal Use Cases:**
❌ Testing websites without explicit permission  
❌ Credential stuffing attacks on third-party services  
❌ Unauthorized access attempts  
❌ Any activity violating Computer Fraud and Abuse Act (CFAA) or equivalent laws  

### **Your Responsibilities:**

1. **Obtain written authorization** before testing any system you don't own
2. **Respect rate limits** and terms of service
3. **Use responsibly** and ethically
4. **Understand local laws** regarding computer security testing

**⚠️ The authors and contributors of this tool are NOT responsible for any misuse or damage caused by this software. By using this tool, you agree to use it legally and ethically.**

---

## 🛡️ **Ethical Guidelines**

### **Best Practices:**

1. **Always get permission** in writing before testing
2. **Start with low thread counts** (3-5) to avoid overwhelming servers
3. **Respect rate limits** - add delays between requests
4. **Don't test production systems** without proper authorization
5. **Report vulnerabilities responsibly** if you discover them
6. **Use only on isolated test environments** when learning

### **Red Flags (Don't Do This):**

- ❌ Testing random websites "for fun"
- ❌ Using stolen credential lists
- ❌ Attempting to access accounts you don't own
- ❌ Selling or distributing found credentials
- ❌ Ignoring rate limits or anti-bot measures

---

## 🔧 **Troubleshooting**

### **Problem: "No valid credentials found" but I know they're valid**

**Possible causes:**
1. Wrong form field names (check with DevTools)
2. CSRF token required (tool doesn't handle this yet)
3. JavaScript-based login (tool only handles standard POST)
4. Captcha/bot detection active

**Solution**: Double-check field names and login endpoint URL.

---

### **Problem: Getting IP banned after a few attempts**

**Possible causes:**
1. Too many threads
2. Too fast (low delay between requests)
3. Site has aggressive rate limiting

**Solution**:
- Reduce threads to 3-5
- Increase delay to 3-5 seconds
- Consider using proxies (advanced, not covered)

---

### **Problem: All credentials showing as "potential hits"**

**Possible causes:**
1. Site returns different responses for each request (dynamic content)
2. Session cookies not being handled properly
3. Login endpoint incorrect

**Solution**: 
- Check if calibration shows consistent responses
- Verify you're using the correct POST endpoint

---

### **Problem: "ModuleNotFoundError: No module named 'requests'"**

**Solution**:
```bash
pip install requests
```

---

## 📊 **Performance Benchmarks**

Tested on: MacBook Pro M1, Python 3.9, 1000 credentials

| Configuration | Speed | Notes |
|--------------|-------|-------|
| 1 thread, 2s delay | ~0.5 creds/sec | Safest, slowest |
| 3 threads, 2s delay | ~1.5 creds/sec | Recommended for testing |
| 5 threads, 2s delay | ~2.5 creds/sec | Good balance |
| 10 threads, 1s delay | ~10 creds/sec | Fast but risky |
| 20 threads, 0.5s delay | ~40 creds/sec | High ban risk |

**Recommendation**: Start with 3-5 threads, monitor for blocks, then adjust.

---

## 🤝 **Contributing**

Contributions are welcome! Here's how you can help:

### **Areas for Improvement:**

1. **CSRF Token Handling**: Automatically extract and include CSRF tokens
2. **Proxy Rotation**: Add support for rotating proxy lists
3. **Captcha Detection**: Detect when captcha is triggered
4. **JavaScript Rendering**: Support for JavaScript-heavy login pages
5. **GUI Interface**: Desktop application with visual interface
6. **Database Support**: Store results in SQLite instead of text files

### **How to Contribute:**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Code Style:**

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where appropriate
- Write clear commit messages

---

## 📚 **Resources & Learning**

### **Recommended Reading:**

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Burp Suite Documentation](https://portswigger.net/burp/documentation)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Python Threading Guide](https://docs.python.org/3/library/threading.html)

### **Similar Tools (for reference):**

- **Hydra**: Multi-protocol brute force tool
- **Medusa**: Parallel login brute-forcer
- **Burp Intruder**: GUI-based testing tool
- **Patator**: Multi-purpose brute-forcer

---

## 🏆 **Credits**

**Developed by**: Prince.  
**Project Type**: Educational Security Research Tool  
**License**: MIT License (see below)  

### **Special Thanks:**

- OWASP for security testing guidelines
- Python requests library maintainers
- Security research community

---

## 📄 **License**

```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 **Contact & Support**

- **GitHub Issues**: [Report bugs or request features](https://github.com/Dark5301/credential-testing-tool/issues)
- **Email**: ps9488348@gmail.com

---

## 🌟 **Star This Project**

If you found this tool useful for learning about security testing, please consider giving it a ⭐ on GitHub!

---

## 🔮 **Future Roadmap**

- [ ] CSRF token extraction
- [ ] Proxy rotation support
- [ ] GUI interface
- [ ] Docker containerization
- [ ] API rate limit detection
- [ ] Captcha detection
- [ ] Session persistence
- [ ] Custom success detection rules
- [ ] Export results to JSON/CSV
- [ ] Real-time progress dashboard

---

**Last Updated**: February 2025  
**Version**: 1.0.0  
**Status**: Active Development

---

<p align="center">
  Made with ❤️ for the security research community
</p>

<p align="center">
  <strong>Use responsibly. Test ethically. Learn continuously.</strong>
</p>
