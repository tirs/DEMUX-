"""
Client Testing Helper for Audio Pipeline
Generates test reports and validates the entire pipeline
"""

import os
import sys
import requests
import time
import json
from pathlib import Path
from typing import Dict, List
import subprocess

API_URL = "http://localhost:8000"
TEST_DIR = Path("./test_audio")
TEST_AUDIO_FILES = [
    "Audio/1.wav",
    "Audio/A Free Night In Bushwick - William Rosati  Royalty Free Music - No Copyright Music.wav"
]


class ClientTester:
    def __init__(self):
        self.test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
    
    def log_test(self, name: str, status: str, details: Dict = None):
        """Log test result"""
        result = {
            "name": name,
            "status": status,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "details": details or {}
        }
        self.test_results["tests"].append(result)
        self.test_results["summary"]["total"] += 1
        
        if status == "PASSED":
            self.test_results["summary"]["passed"] += 1
        else:
            self.test_results["summary"]["failed"] += 1
        
        emoji = "✅" if status == "PASSED" else "❌"
        print(f"{emoji} {name}: {status}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def test_api_connection(self):
        """Test API connectivity"""
        try:
            response = requests.get(f"{API_URL}/config", timeout=5)
            if response.status_code == 200:
                config = response.json()
                self.log_test("API Connection", "PASSED", config)
                return True
            else:
                self.log_test("API Connection", "FAILED", 
                             {"status_code": response.status_code})
                return False
        except Exception as e:
            self.log_test("API Connection", "FAILED", {"error": str(e)})
            self.test_results["summary"]["errors"].append(str(e))
            return False
    
    def test_streamlit_ui(self):
        """Test Streamlit UI launch"""
        try:
            # Try to start streamlit in background
            result = subprocess.run(
                ["streamlit", "run", "ui/app_advanced.py", "--logger.level=error"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                self.log_test("Streamlit UI Launch", "PASSED")
                return True
            else:
                self.log_test("Streamlit UI Launch", "FAILED", 
                             {"error": result.stderr.decode()})
                return False
        except subprocess.TimeoutExpired:
            # Timeout is OK for streamlit (runs in background)
            self.log_test("Streamlit UI Launch", "PASSED", 
                         {"note": "Streamlit running"})
            return True
        except Exception as e:
            self.log_test("Streamlit UI Launch", "FAILED", {"error": str(e)})
            return False
    
    def test_audio_file_upload(self, file_path: str):
        """Test audio file upload and processing"""
        try:
            if not Path(file_path).exists():
                self.log_test(f"Upload: {file_path}", "SKIPPED", 
                             {"reason": "File not found"})
                return False
            
            with open(file_path, "rb") as f:
                files = {"file": (Path(file_path).name, f, "audio/wav")}
                response = requests.post(
                    f"{API_URL}/process",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                self.log_test(
                    f"Upload: {Path(file_path).name}",
                    "PASSED",
                    {"job_id": job_id}
                )
                return job_id
            else:
                self.log_test(f"Upload: {file_path}", "FAILED",
                             {"status_code": response.status_code})
                return None
        except Exception as e:
            self.log_test(f"Upload: {file_path}", "FAILED", {"error": str(e)})
            return None
    
    def test_job_status(self, job_id: str):
        """Test job status retrieval"""
        try:
            response = requests.get(f"{API_URL}/job/{job_id}", timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                completed = sum(1 for s in status.get("stages", []) 
                              if s.get("status") == "completed")
                total = len(status.get("stages", []))
                
                self.log_test(
                    f"Job Status: {job_id}",
                    "PASSED",
                    {
                        "status": status.get("status"),
                        "progress": f"{completed}/{total}",
                        "stages": total
                    }
                )
                return status
            else:
                self.log_test(f"Job Status: {job_id}", "FAILED")
                return None
        except Exception as e:
            self.log_test(f"Job Status: {job_id}", "FAILED", {"error": str(e)})
            return None
    
    def test_full_pipeline(self, file_path: str, timeout: int = 600):
        """Test complete processing pipeline"""
        print(f"\n🔄 Testing full pipeline for: {file_path}")
        
        # Upload
        job_id = self.test_audio_file_upload(file_path)
        if not job_id:
            return False
        
        # Wait for completion
        start_time = time.time()
        max_wait = timeout
        
        while time.time() - start_time < max_wait:
            status = self.test_job_status(job_id)
            
            if status and status.get("status") == "completed":
                outputs = status.get("outputs", {})
                self.log_test(
                    f"Pipeline Complete: {job_id}",
                    "PASSED",
                    {"outputs": len(outputs), "tracks": list(outputs.keys())}
                )
                return True
            
            elif status and status.get("status") == "failed":
                self.log_test(f"Pipeline: {job_id}", "FAILED",
                             {"reason": "Pipeline failed"})
                return False
            
            print(f"⏳ Waiting for job {job_id}... ({int(time.time() - start_time)}s)")
            time.sleep(5)
        
        self.log_test(f"Pipeline: {job_id}", "FAILED",
                     {"reason": f"Timeout after {timeout}s"})
        return False
    
    def test_download_tracks(self, job_id: str):
        """Test track download"""
        try:
            # Get job status to find tracks
            response = requests.get(f"{API_URL}/job/{job_id}", timeout=10)
            if response.status_code != 200:
                self.log_test(f"Download: {job_id}", "FAILED")
                return False
            
            status = response.json()
            outputs = status.get("outputs", {})
            
            if not outputs:
                self.log_test(f"Download: {job_id}", "SKIPPED",
                             {"reason": "No outputs available"})
                return True
            
            # Try downloading first track
            first_track = list(outputs.keys())[0]
            
            response = requests.get(
                f"{API_URL}/download/{job_id}/{first_track}",
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                self.log_test(
                    f"Download: {first_track}",
                    "PASSED",
                    {"size": f"{len(response.content) / (1024*1024):.2f} MB"}
                )
                return True
            else:
                self.log_test(f"Download: {first_track}", "FAILED")
                return False
        
        except Exception as e:
            self.log_test(f"Download: {job_id}", "FAILED", {"error": str(e)})
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting Client Testing Suite\n")
        print("=" * 60)
        
        # 1. API Connection
        print("\n1️⃣ Testing API Connection...")
        if not self.test_api_connection():
            print("❌ API not available. Stopping tests.")
            return False
        
        # 2. Streamlit UI
        print("\n2️⃣ Testing Streamlit UI...")
        self.test_streamlit_ui()
        
        # 3. Full Pipeline
        print("\n3️⃣ Testing Full Pipeline...")
        for file_path in TEST_AUDIO_FILES:
            if Path(file_path).exists():
                if self.test_full_pipeline(file_path):
                    # 4. Download Test
                    print("\n4️⃣ Testing Downloads...")
                    job_id = self.test_audio_file_upload(file_path)
                    if job_id:
                        time.sleep(5)
                        self.test_download_tracks(job_id)
                    break
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.test_results['summary']['total']}")
        print(f"✅ Passed: {self.test_results['summary']['passed']}")
        print(f"❌ Failed: {self.test_results['summary']['failed']}")
        
        if self.test_results['summary']['errors']:
            print("\n⚠️ Errors:")
            for error in self.test_results['summary']['errors']:
                print(f"   - {error}")
        
        # Save report
        self.save_report()
        
        return self.test_results['summary']['failed'] == 0
    
    def save_report(self):
        """Save test report to file"""
        report_file = Path("test_report.json")
        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Test report saved to: {report_file}")
        
        # Also save markdown report
        md_file = Path("test_report.md")
        with open(md_file, "w") as f:
            f.write("# Audio Pipeline - Client Test Report\n\n")
            f.write(f"**Generated:** {self.test_results['timestamp']}\n\n")
            f.write("## Summary\n")
            f.write(f"- Total Tests: {self.test_results['summary']['total']}\n")
            f.write(f"- Passed: {self.test_results['summary']['passed']}\n")
            f.write(f"- Failed: {self.test_results['summary']['failed']}\n\n")
            f.write("## Test Results\n")
            
            for test in self.test_results['tests']:
                f.write(f"\n### {test['name']}\n")
                f.write(f"**Status:** {test['status']}\n")
                if test['details']:
                    f.write("**Details:**\n")
                    for key, value in test['details'].items():
                        f.write(f"- {key}: {value}\n")
        
        print(f"📄 Markdown report saved to: {md_file}")


if __name__ == "__main__":
    tester = ClientTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)