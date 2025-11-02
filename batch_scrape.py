from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key="fc-bcff4efba96147fcbf6fec3b7d80b246")


job = firecrawl.batch_scrape([
    "https://firecrawl.dev",
    "https://docs.firecrawl.dev",
], formats=["markdown"], poll_interval=2, wait_timeout=120)

print(job.status, job.completed, job.total)