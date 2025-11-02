"""
Test that we can now map all URLs from sendoso.com (should be 1088 URLs)
"""
import os
from dotenv import load_dotenv
from utils.firecrawl_helpers import map_website

load_dotenv()

print("=" * 80)
print("TEST: Mapping sendoso.com with new limit=5000 config")
print("=" * 80)
print()

# Test mapping sendoso.com
result = map_website("https://sendoso.com")

print(f"Result:")
print(f"  success: {result['success']}")
print(f"  domain: {result['domain']}")
print(f"  total_urls: {result['total_urls']}")

if result['success']:
    print(f"\n✅ SUCCESS! Mapped {result['total_urls']} URLs from sendoso.com")
    if result['total_urls'] >= 1000:
        print(f"   This confirms we're now capturing all ~1088 URLs!")
    elif result['total_urls'] > 100:
        print(f"   This is better than the previous 84-100 URL limit")
    else:
        print(f"   ⚠️  Still seems low - expected 1088 URLs")

    # Show first 10 URLs as sample
    print(f"\nFirst 10 URLs:")
    for i, url in enumerate(result['urls'][:10], 1):
        print(f"  {i}. {url}")
else:
    print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
