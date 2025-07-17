#!/usr/bin/env python3
"""
Test script for TikTok vm.tiktok.com URL functionality
"""

import requests
import json

def test_tiktok_vm_urls():
    """Test TikTok vm.tiktok.com URL analysis"""
    
    # Test URLs - replace with actual TikTok URLs
    test_urls = [
        "https://vm.tiktok.com/ZNdavRDxy/",  # Your example URL
        "https://vt.tiktok.com/ZSExample/",  # Alternative short format
        "https://www.tiktok.com/@user/video/1234567890123456789",  # Regular TikTok URL
    ]
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing TikTok vm.tiktok.com Analysis...")
    print("=" * 60)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🎯 Test {i}: {url}")
        print("-" * 50)
        
        try:
            # Test the analyze endpoint
            response = requests.post(
                f"{base_url}/api/analyze",
                json={"url": url},
                timeout=45  # Longer timeout for TikTok processing
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"   Platform: {data.get('platform')}")
                print(f"   Title: {data.get('title', 'N/A')}")
                print(f"   Duration: {data.get('duration', 'N/A')} seconds")
                print(f"   Thumbnail: {'✅' if data.get('thumbnail') else '❌'}")
                print(f"   Formats: {len(data.get('formats', []))} available")
                
                # Test download if analysis succeeded
                if data.get('platform') == 'tiktok':
                    print(f"\n🔽 Testing download...")
                    download_response = requests.post(
                        f"{base_url}/api/download",
                        json={
                            "url": url,
                            "quality": "default",
                            "format": "video"
                        },
                        timeout=60
                    )
                    
                    if download_response.status_code == 200:
                        download_data = download_response.json()
                        print(f"   Download: ✅ Success!")
                        print(f"   Filename: {download_data.get('filename', 'N/A')}")
                        print(f"   Size: {download_data.get('filesize', 'N/A')} bytes")
                    else:
                        print(f"   Download: ❌ Failed ({download_response.status_code})")
                        try:
                            error_data = download_response.json()
                            print(f"   Error: {error_data.get('error', 'Unknown error')}")
                        except:
                            print(f"   Error: {download_response.text}")
                            
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
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

def test_url_resolution():
    """Test URL resolution functionality directly"""
    print("\n🔧 Testing URL Resolution...")
    print("-" * 40)
    
    from tiktok_downloader import TikTokDownloader
    
    downloader = TikTokDownloader()
    test_url = "https://vm.tiktok.com/ZNdavRDxy/"
    
    try:
        resolved = downloader.resolve_shortened_url(test_url)
        print(f"Original:  {test_url}")
        print(f"Resolved:  {resolved}")
        print(f"Changed:   {'✅' if resolved != test_url else '❌'}")
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")

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
    print("🚀 TikTok vm.tiktok.com Test Suite")
    print("=" * 60)
    
    # Test URL resolution first
    test_url_resolution()
    
    if check_server():
        test_tiktok_vm_urls()
    else:
        print("\n🔧 To start the server:")
        print("   1. source venv/bin/activate")
        print("   2. python app.py")
        print("   3. Run this test again")