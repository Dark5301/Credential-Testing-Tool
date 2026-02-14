from request_architect import RequestArchitect
import time

class Calibrator:
    def __init__(self, login_url, username_field='username', password_field='password'):
        """
        Initialize the calibrator with RequestArchitect built-in
        
        Args:
            login_url: The login endpoint URL
            username_field: Name of the username field in the form
            password_field: Name of the password field in the form
        """
        self.architect = RequestArchitect()
        self.session = self.architect.session
        self.login_url = login_url
        self.username_field = username_field
        self.password_field = password_field
        self.calibration_responses = []
    
    def run_calibration(self, num_attempts=5, delay=2):
        """
        Send fake login attempts to establish baseline
        
        Args:
            num_attempts: Number of calibration attempts (default: 5)
            delay: Seconds to wait between attempts (default: 2)
        """
        print("=" * 60)
        print("CALIBRATION PHASE: Establishing failure pattern")
        print("=" * 60)
        
        fake_credentials = [
            ('INVALID_USER_12345', 'WRONG_PASSWORD_67890'),
            ('NONEXISTENT_ACCOUNT_XYZ', 'FAKE_PASS_ABC'),
            ('CALIBRATION_TEST_USER_1', 'INVALID_CREDENTIAL_1'),
            ('DOES_NOT_EXIST_USER', 'WRONG_PASS_12345'),
            ('FAKE_ACCOUNT_TEST', 'BAD_PASSWORD_XYZ'),
        ]
        
        for i in range(num_attempts):
            username, password = fake_credentials[i]
            
            # Create login data
            login_data = {
                self.username_field: username,
                self.password_field: password
            }
            
            # Send POST request
            response = self.session.post(self.login_url, data=login_data)
            
            # Store response
            self.calibration_responses.append(response)
            
            # Print progress
            print(f"Calibration {i+1}/{num_attempts}:")
            print(f"  Status: {response.status_code}")
            print(f"  Length: {len(response.text)} bytes")
            print(f"  URL: {response.url}")
            
            # Sleep between attempts (except last one)
            if i < num_attempts - 1:
                time.sleep(delay)
        
        print(f"\n✓ Calibration complete! Collected {len(self.calibration_responses)} baseline responses")

class PatternAnalyzer:
    def __init__(self, calibration_responses):
        """
        Analyze calibration responses to find failure pattern
        
        Args:
            calibration_responses: List of response objects from calibration
        """
        self.responses = calibration_responses
        self.pattern = {}
    
    def analyze(self):
        """
        Find what's consistent across all calibration responses
        """
        print("\n" + "=" * 60)
        print("PATTERN ANALYSIS: Finding failure signature")
        print("=" * 60)
        
        # Extract features from all responses
        status_codes = [r.status_code for r in self.responses]
        lengths = [len(r.text) for r in self.responses]
        urls = [r.url for r in self.responses]
        
        # Print what we found
        print(f"\nStatus codes: {status_codes}")
        print(f"Response lengths: {lengths}")
        print(f"URLs: {set(urls)}")
        
        # Build the failure pattern
        self.pattern = {
            'status_code': status_codes[0] if len(set(status_codes)) == 1 else None,
            'length_min': min(lengths) - 50,  # Allow 50 byte variance
            'length_max': max(lengths) + 50,
            'url': urls[0] if len(set(urls)) == 1 else None,
        }
        
        print("\n✓ Failure Pattern Identified:")
        print(f"  Expected Status: {self.pattern['status_code']}")
        print(f"  Expected Length Range: {self.pattern['length_min']}-{self.pattern['length_max']} bytes")
        print(f"  Expected URL: {self.pattern['url']}")
        
        return self.pattern
    
    def get_pattern(self):
        """Return the identified pattern"""
        return self.pattern
    
class LoginDetector:
    def __init__(self, calibrator, pattern_analyzer):
        """
        Detect successful logins by comparing against failure pattern
        
        Args:
            calibrator: Calibrator object (for session access)
            pattern_analyzer: PatternAnalyzer object (for failure pattern)
        """
        self.calibrator = calibrator
        self.session = calibrator.session
        self.login_url = calibrator.login_url
        self.username_field = calibrator.username_field
        self.password_field = calibrator.password_field
        self.failure_pattern = pattern_analyzer.get_pattern()
    
    def test_credential(self, username, password):
        """
        Test a single credential and determine if login succeeded
        
        Args:
            username: Username to test
            password: Password to test
            
        Returns:
            tuple: (is_success, response, deviation_score, reasons)
        """
        # Send login request
        login_data = {
            self.username_field: username,
            self.password_field: password
        }
        response = self.session.post(self.login_url, data=login_data)
        
        # Compare against failure pattern
        deviations = []
        score = 0
        
        # Check status code
        if self.failure_pattern['status_code'] and response.status_code != self.failure_pattern['status_code']:
            score += 3
            deviations.append(f"Status changed: {self.failure_pattern['status_code']} → {response.status_code}")
        
        # Check response length
        response_length = len(response.text)
        if not (self.failure_pattern['length_min'] <= response_length <= self.failure_pattern['length_max']):
            score += 2
            deviations.append(f"Length anomaly: {response_length} bytes (expected {self.failure_pattern['length_min']}-{self.failure_pattern['length_max']})")
        
        # Check URL (redirect detection)
        if self.failure_pattern['url'] and response.url != self.failure_pattern['url']:
            score += 3
            deviations.append(f"Redirected: {self.failure_pattern['url']} → {response.url}")
        
        # Determine success (score >= 3 = likely success)
        is_success = score >= 3
        
        return (is_success, response, score, deviations)
    
    def print_result(self, username, password, is_success, score, deviations):
        """Pretty print the test result"""
        if is_success:
            print(f"\n🎯 POTENTIAL HIT: {username}:{password}")
            print(f"   Deviation Score: {score}/8")
            for reason in deviations:
                print(f"   - {reason}")
        else:
            print(f"   ❌ Failed: {username}:{password} (matches failure pattern)")

# Test it
if __name__ == "__main__":
    # Step 1: Calibration
    calibrator = Calibrator('https://httpbin.org/post')
    calibrator.run_calibration()
    
    # Step 2: Pattern Analysis
    analyzer = PatternAnalyzer(calibrator.calibration_responses)
    failure_pattern = analyzer.analyze()
    
    # Step 3: Create Detector
    detector = LoginDetector(calibrator, analyzer)
    
    # Step 4: Test some credentials
    print("\n" + "=" * 60)
    print("TESTING CREDENTIALS")
    print("=" * 60)
    
    # Test credentials that match failure pattern
    test_creds = [
        ('test_user_1', 'test_pass_1'),
        ('test_user_2', 'test_pass_2'),
    ]
    
    for username, password in test_creds:
        is_success, response, score, deviations = detector.test_credential(username, password)
        detector.print_result(username, password, is_success, score, deviations)
    
    # NOW: Simulate a successful login by changing the endpoint temporarily
    print("\n" + "=" * 60)
    print("SIMULATING A SUCCESSFUL LOGIN (different response)")
    print("=" * 60)
    
    # Temporarily change URL to simulate redirect
    original_url = detector.login_url
    detector.login_url = 'https://httpbin.org/status/302'  # This returns 302 (redirect)
    
    is_success, response, score, deviations = detector.test_credential('potential_valid_user', 'potential_valid_pass')
    detector.print_result('potential_valid_user', 'potential_valid_pass', is_success, score, deviations)
    
    # Restore original URL
    detector.login_url = original_url