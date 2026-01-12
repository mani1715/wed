#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Wedding Invitation Platform
Tests all authentication, profile management, media, and public invitation APIs
"""

import requests
import json
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔗 Testing backend at: {API_BASE}")

class WeddingAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_profile_id = None
        self.test_slug = None
        self.test_media_id = None
        self.test_greeting_id = None
        
    def log_test(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if not success:
            print()
    
    def test_admin_login(self):
        """Test admin authentication"""
        print("\n🔐 Testing Authentication...")
        
        # Test login with correct credentials
        login_data = {
            "email": "admin@wedding.com",
            "password": "admin123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "admin" in data:
                    self.admin_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_test("Admin Login", True, f"Token received, Admin ID: {data['admin']['id']}")
                    return True
                else:
                    self.log_test("Admin Login", False, "Missing token or admin info in response")
                    return False
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_login_invalid(self):
        """Test login with invalid credentials"""
        invalid_login = {
            "email": "admin@wedding.com",
            "password": "wrongpassword"
        }
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=invalid_login)
            
            if response.status_code == 401:
                self.log_test("Invalid Login Rejection", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_test("Invalid Login Rejection", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Login Rejection", False, f"Exception: {str(e)}")
            return False
    
    def test_auth_me(self):
        """Test /auth/me endpoint"""
        if not self.admin_token:
            self.log_test("Auth Me Endpoint", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data:
                    self.log_test("Auth Me Endpoint", True, f"Admin info retrieved: {data['email']}")
                    return True
                else:
                    self.log_test("Auth Me Endpoint", False, "Missing required fields in response")
                    return False
            else:
                self.log_test("Auth Me Endpoint", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Auth Me Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_create_profile(self):
        """Test profile creation"""
        print("\n👰 Testing Profile Management...")
        
        if not self.admin_token:
            self.log_test("Create Profile", False, "No admin token available")
            return False
        
        # Create a realistic wedding profile
        profile_data = {
            "groom_name": "Rajesh Kumar",
            "bride_name": "Priya Sharma",
            "event_type": "marriage",
            "event_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "venue": "Grand Palace Hotel, Mumbai",
            "language": "english",
            "sections_enabled": {
                "opening": True,
                "welcome": True,
                "couple": True,
                "photos": True,
                "video": False,
                "events": True,
                "greetings": True,
                "footer": True
            },
            "link_expiry_type": "permanent",
            "link_expiry_value": None
        }
        
        try:
            response = self.session.post(f"{API_BASE}/admin/profiles", json=profile_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "slug" in data and "invitation_link" in data:
                    self.test_profile_id = data["id"]
                    self.test_slug = data["slug"]
                    self.log_test("Create Profile", True, f"Profile created with slug: {data['slug']}")
                    return True
                else:
                    self.log_test("Create Profile", False, "Missing required fields in response")
                    return False
            else:
                self.log_test("Create Profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_get_all_profiles(self):
        """Test getting all profiles"""
        if not self.admin_token:
            self.log_test("Get All Profiles", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/admin/profiles")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Profiles", True, f"Retrieved {len(data)} profiles")
                    return True
                else:
                    self.log_test("Get All Profiles", False, "Response is not a list")
                    return False
            else:
                self.log_test("Get All Profiles", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get All Profiles", False, f"Exception: {str(e)}")
            return False
    
    def test_get_single_profile(self):
        """Test getting single profile"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Get Single Profile", False, "No admin token or profile ID available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/admin/profiles/{self.test_profile_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.test_profile_id:
                    self.log_test("Get Single Profile", True, f"Retrieved profile: {data['groom_name']} & {data['bride_name']}")
                    return True
                else:
                    self.log_test("Get Single Profile", False, "Profile ID mismatch or missing data")
                    return False
            else:
                self.log_test("Get Single Profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Single Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_update_profile(self):
        """Test profile update"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Update Profile", False, "No admin token or profile ID available")
            return False
        
        update_data = {
            "venue": "Updated Venue - Taj Palace, Delhi",
            "language": "hindi"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/admin/profiles/{self.test_profile_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("venue") == update_data["venue"] and data.get("language") == update_data["language"]:
                    self.log_test("Update Profile", True, f"Profile updated successfully")
                    return True
                else:
                    self.log_test("Update Profile", False, "Update data not reflected in response")
                    return False
            else:
                self.log_test("Update Profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_add_media(self):
        """Test adding media to profile"""
        print("\n📸 Testing Media Management...")
        
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Add Media", False, "No admin token or profile ID available")
            return False
        
        media_data = {
            "media_type": "photo",
            "media_url": "https://example.com/wedding-photo1.jpg",
            "caption": "Beautiful couple photo",
            "order": 1
        }
        
        try:
            response = self.session.post(f"{API_BASE}/admin/profiles/{self.test_profile_id}/media", json=media_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("media_url") == media_data["media_url"]:
                    self.test_media_id = data["id"]
                    self.log_test("Add Media", True, f"Media added with ID: {data['id']}")
                    return True
                else:
                    self.log_test("Add Media", False, "Missing ID or URL mismatch in response")
                    return False
            else:
                self.log_test("Add Media", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add Media", False, f"Exception: {str(e)}")
            return False
    
    def test_get_profile_media(self):
        """Test getting profile media"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Get Profile Media", False, "No admin token or profile ID available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/admin/profiles/{self.test_profile_id}/media")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Get Profile Media", True, f"Retrieved {len(data)} media items")
                    return True
                else:
                    self.log_test("Get Profile Media", False, "No media items found or invalid response")
                    return False
            else:
                self.log_test("Get Profile Media", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Profile Media", False, f"Exception: {str(e)}")
            return False
    
    def test_public_invitation(self):
        """Test public invitation access"""
        print("\n💌 Testing Public Invitation APIs...")
        
        if not self.test_slug:
            self.log_test("Public Invitation Access", False, "No test slug available")
            return False
        
        try:
            # Use a new session without auth headers for public access
            public_session = requests.Session()
            response = public_session.get(f"{API_BASE}/invite/{self.test_slug}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["slug", "groom_name", "bride_name", "event_type", "event_date", "venue", "media", "greetings"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Public Invitation Access", True, f"Invitation data retrieved for {data['groom_name']} & {data['bride_name']}")
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Public Invitation Access", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Public Invitation Access", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Public Invitation Access", False, f"Exception: {str(e)}")
            return False
    
    def test_submit_greeting(self):
        """Test submitting a guest greeting"""
        if not self.test_slug:
            self.log_test("Submit Greeting", False, "No test slug available")
            return False
        
        greeting_data = {
            "guest_name": "Amit Patel",
            "message": "Congratulations on your special day! Wishing you both a lifetime of happiness and love. May your marriage be filled with joy, laughter, and endless blessings."
        }
        
        try:
            # Use a new session without auth headers for public access
            public_session = requests.Session()
            response = public_session.post(f"{API_BASE}/invite/{self.test_slug}/greetings", json=greeting_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("guest_name") == greeting_data["guest_name"]:
                    self.test_greeting_id = data["id"]
                    self.log_test("Submit Greeting", True, f"Greeting submitted by {data['guest_name']}")
                    return True
                else:
                    self.log_test("Submit Greeting", False, "Missing ID or name mismatch in response")
                    return False
            else:
                self.log_test("Submit Greeting", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Submit Greeting", False, f"Exception: {str(e)}")
            return False
    
    def test_get_profile_greetings(self):
        """Test getting profile greetings as admin"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Get Profile Greetings", False, "No admin token or profile ID available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/admin/profiles/{self.test_profile_id}/greetings")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Get Profile Greetings", True, f"Retrieved {len(data)} greetings")
                    return True
                else:
                    self.log_test("Get Profile Greetings", False, "No greetings found or invalid response")
                    return False
            else:
                self.log_test("Get Profile Greetings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Profile Greetings", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_media(self):
        """Test deleting media"""
        if not self.admin_token or not self.test_media_id:
            self.log_test("Delete Media", False, "No admin token or media ID available")
            return False
            
        try:
            response = self.session.delete(f"{API_BASE}/admin/media/{self.test_media_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Delete Media", True, "Media deleted successfully")
                    return True
                else:
                    self.log_test("Delete Media", False, "No success message in response")
                    return False
            else:
                self.log_test("Delete Media", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Media", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_profile(self):
        """Test profile deletion (soft delete)"""
        if not self.admin_token or not self.test_profile_id:
            self.log_test("Delete Profile", False, "No admin token or profile ID available")
            return False
            
        try:
            response = self.session.delete(f"{API_BASE}/admin/profiles/{self.test_profile_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Delete Profile", True, "Profile soft deleted successfully")
                    return True
                else:
                    self.log_test("Delete Profile", False, "No success message in response")
                    return False
            else:
                self.log_test("Delete Profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_expired_link_access(self):
        """Test accessing deleted/expired profile"""
        if not self.test_slug:
            self.log_test("Expired Link Access", False, "No test slug available")
            return False
            
        try:
            # Use a new session without auth headers for public access
            public_session = requests.Session()
            response = public_session.get(f"{API_BASE}/invite/{self.test_slug}")
            
            if response.status_code == 410:
                self.log_test("Expired Link Access", True, "Correctly returned 410 for expired/deleted profile")
                return True
            else:
                self.log_test("Expired Link Access", False, f"Expected 410, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Expired Link Access", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Wedding Invitation Platform Backend API Tests")
        print("=" * 60)
        
        test_results = []
        
        # Authentication Tests
        test_results.append(self.test_admin_login())
        test_results.append(self.test_admin_login_invalid())
        test_results.append(self.test_auth_me())
        
        # Profile Management Tests
        test_results.append(self.test_create_profile())
        test_results.append(self.test_get_all_profiles())
        test_results.append(self.test_get_single_profile())
        test_results.append(self.test_update_profile())
        
        # Media Management Tests
        test_results.append(self.test_add_media())
        test_results.append(self.test_get_profile_media())
        
        # Public Invitation Tests
        test_results.append(self.test_public_invitation())
        test_results.append(self.test_submit_greeting())
        test_results.append(self.test_get_profile_greetings())
        
        # Cleanup Tests
        test_results.append(self.test_delete_media())
        test_results.append(self.test_delete_profile())
        test_results.append(self.test_expired_link_access())
        
        # Summary
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "=" * 60)
        print(f"🏁 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Backend APIs are working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Please check the issues above.")
            return False

def main():
    """Main test execution"""
    tester = WeddingAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Backend testing completed successfully!")
        exit(0)
    else:
        print("\n❌ Backend testing completed with failures!")
        exit(1)

if __name__ == "__main__":
    main()