#!/usr/bin/env python3
"""
Debug script for TikTok URL content analysis
"""

from tiktok_downloader import TikTokDownloader
import re

def debug_tiktok_url():
    """Debug TikTok URL content"""
    downloader = TikTokDownloader()
    url = "https://vm.tiktok.com/ZNdavRDxy/"
    
    print("🔍 Debug TikTok URL Processing")
    print("=" * 50)
    
    # Step 1: URL Resolution
    print(f"1. Original URL: {url}")
    resolved_url = downloader.resolve_shortened_url(url)
    print(f"2. Resolved URL: {resolved_url}")
    
    # Step 2: Get content
    try:
        print("\n3. Fetching content...")
        content = downloader.get_content(resolved_url)
        print(f"   Content length: {len(content)} characters")
        
        # Step 3: Look for script tags
        print("\n4. Looking for script tags...")
        script_patterns = [
            r'<script id="__NEXT_DATA__" type="application/json">',
            r'<script id="SIGI_STATE" type="application/json">',
            r'window\.__INITIAL_STATE__',
            r'window\.__DEFAULT_SCOPE__',
            r'window\.SIGI_STATE'
        ]
        
        for pattern in script_patterns:
            matches = re.findall(pattern, content)
            print(f"   {pattern}: {'✅' if matches else '❌'} ({len(matches)} matches)")
        
        # Step 4: Look for video URLs
        print("\n5. Looking for video URLs...")
        video_patterns = [
            r'"playAddr":"([^"]+)"',
            r'"downloadAddr":"([^"]+)"',
            r'"playURL":"([^"]+)"',
            r'https://[^"]*\.mp4[^"]*'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, content)
            print(f"   {pattern}: {'✅' if matches else '❌'} ({len(matches)} matches)")
            if matches:
                for match in matches[:3]:  # Show first 3 matches
                    print(f"      → {match[:100]}...")
        
        # Step 5: Look for title
        print("\n6. Looking for title...")
        title_patterns = [
            r'"desc":"([^"]+)"',
            r'"title":"([^"]+)"',
            r'<title>([^<]+)</title>'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, content)
            print(f"   {pattern}: {'✅' if matches else '❌'} ({len(matches)} matches)")
            if matches:
                print(f"      → {matches[0][:100]}...")
        
        # Step 6: Save content for manual inspection
        with open('debug_content.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n7. Content saved to 'debug_content.html' for manual inspection")
        
    except Exception as e:
        print(f"❌ Error fetching content: {e}")

if __name__ == "__main__":
    debug_tiktok_url()