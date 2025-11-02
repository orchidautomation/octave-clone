"""Test with EXACT example from user - copy/paste"""
import os
from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

# EXACT code from example (with our API key)
firecrawl = Firecrawl(api_key=api_key)

print("=" * 80)
print("TEST: EXACT USER-PROVIDED EXAMPLE")
print("=" * 80)
print("\nUsing exact code from example:")
print("job = firecrawl.batch_scrape([")
print('    "https://firecrawl.dev",')
print('    "https://docs.firecrawl.dev",')
print('], formats=["markdown"], poll_interval=2, timeout=120)')
print()

# Use the waiter method - blocks until completion
job = firecrawl.batch_scrape([
    "https://firecrawl.dev",
    "https://docs.firecrawl.dev",
], formats=["markdown"], poll_interval=2, timeout=120)

print(f"Result:")
print(f"  job.status: {job.status}")
print(f"  job.completed: {job.completed}")
print(f"  job.total: {job.total}")

if hasattr(job, 'data'):
    print(f"  job.data length: {len(job.data)}")
    if len(job.data) > 0:
        print(f"\n✅ SUCCESS! Got {len(job.data)} results")
        for i, doc in enumerate(job.data, 1):
            url = doc.metadata.source_url if hasattr(doc, 'metadata') and doc.metadata else "unknown"
            markdown_len = len(doc.markdown) if hasattr(doc, 'markdown') else 0
            print(f"  {i}. {url} ({markdown_len} chars)")
    else:
        print(f"\n⚠️  FAILED - data is empty")
        print(f"  This is the same bug we've been seeing")

if hasattr(job, 'credits_used'):
    print(f"  job.credits_used: {job.credits_used}")

print("\n" + "=" * 80)
