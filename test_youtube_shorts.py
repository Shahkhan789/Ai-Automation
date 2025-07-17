#!/usr/bin/env python3
"""
Test script for YouTube Shorts functionality
"""

import requests
import json

def test_youtube_shorts():
    """Test YouTube Shorts analysis"""
    
    # Test URLs - you can replace these with actual YouTube Shorts URLs
    test_urls = [
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",  # Example Short URL
        "https://youtube.com/shorts/dQw4w9WgXcQ",     # Alternative format
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ", # Regular video URL
    ]
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing YouTube Shorts Analysis...")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🎯 Test {i}: {url}")
        print("-" * 40)
        
        try:
            # Test the analyze endpoint
            response = requests.post(
                f"{base_url}/api/analyze",
                json={"url": url},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"   Platform: {data.get('platform')}")
                print(f"   Title: {data.get('title', 'N/A')[:50]}...")
                print(f"   Duration: {data.get('duration', 'N/A')} seconds")
                print(f"   Thumbnail: {'✅' if data.get('thumbnail') else '❌'}")
                print(f"   Formats: {len(data.get('formats', []))} available")
                print(f"   Transcript: {'✅' if data.get('transcript_available') else '❌'}")
            else:
                print(f"❌ Failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print("❌ Server responded with error")
            return False
    except:
        print("❌ Server is not running or not accessible")
        print("💡 Please start the server with: python app.py")
        return False

if __name__ == "__main__":
    print("🚀 YouTube Shorts Test Suite")
    print("=" * 50)
    
    if check_server():
        test_youtube_shorts()
    else:
        print("\n🔧 To start the server:")
        print("   1. source venv/bin/activate")
        print("   2. python app.py")
        print("   3. Run this test again")