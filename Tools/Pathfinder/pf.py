#!/usr/bin/env python3
"""
Pathfinder (pf) - simple directory scanner with default importance highlighting
"""
import asyncio
import aiohttp
import argparse
import json
from urllib.parse import urljoin, urlparse

# ANSI colors for terminal
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"
COLOR_BOLD = "\033[1m"

# Default important paths
DEFAULT_INTERESTING = [
    "/robots.txt",
    "/sitemap.xml",
    "/.env",
    "/.git",
    "/wp-config.php",
    "/config.php",
    "/backup.zip",
    "/backup.tar.gz",
    "/admin",
    "/login",
]

# Small default wordlist
DEFAULT_WORDLIST = [
    "admin",
    "login",
    "dashboard",
    "backup",
    "uploads",
    "test",
    "old",
    "dev",
]

# Function to check if a response is interesting
def is_interesting(url, status, content_length):
    # Exact important path match
    for p in DEFAULT_INTERESTING:
        if url.endswith(p) or (p.endswith("/") and url.endswith(p)):
            return 100, f"important-path {p}"
    
    # Now handle status checks safely (only compare numbers when status is int)
    # status may be an int (e.g. 200) or a str like "timeout"/"error"
    if isinstance(status, int):
        if status == 200 and (content_length or 0) > 0:
            return 50, f"200 content_length={content_length}"
        if status in (301, 302):
            return 40, "redirect"
        if status == 401:
            return 30, "auth-required"
        if status == 403:
            return 25, "forbidden"
        if status >= 500:
            return 10, f"server-error {status}"
    # Non-numeric statuses (timouts/conn errors) are low-interest
    return 0, ""

async def fetch(session, url):
    try:
        async with session.get(url, timeout=5) as resp:
            text = await resp.text()
            return {
                "url": url,
                "status": resp.status,
                "content_length": len(text)
            }
    except asyncio.TimeoutError:
        return {"url": url, "status": "timeout", "content_length": None}
    except Exception:
        return {"url": url, "status": "error", "content_length": None}

async def worker(base_url, paths, out_file):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, urljoin(base_url, p)) for p in paths]
        with open(out_file, "w") as out_f:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                score, reason = is_interesting(res["url"], res.get("status"), res.get("content_length") or 0)
                status = res.get("status")
                # Print with color
                if score >= 100:
                    print(f"{COLOR_BOLD}{COLOR_RED}[!!] {res['url']} -> {status} ({reason}){COLOR_RESET}")
                elif score >= 50:
                    print(f"{COLOR_BOLD}{COLOR_YELLOW}[+] {res['url']} -> {status} ({reason}){COLOR_RESET}")
                elif status in (401, 403):
                    print(f"{COLOR_CYAN}[i] {res['url']} -> {status} ({reason}){COLOR_RESET}")
                # Write all responses to file
                out_f.write(json.dumps(res, ensure_ascii=False) + "\n")
                out_f.flush()

def main():
    parser = argparse.ArgumentParser(description="Pathfinder (pf) - simple directory scanner")
    parser.add_argument("--url", required=True, help="Base URL to scan")
    parser.add_argument("--wordlist", help="File containing wordlist (one per line)")
    parser.add_argument("--output", default="pf_results.jsonl", help="Output file")
    args = parser.parse_args()

    # Load wordlist
    if args.wordlist:
        with open(args.wordlist) as f:
            paths = [line.strip() for line in f if line.strip()]
    else:
        paths = DEFAULT_WORDLIST
    
    # Start asyncio worker
    asyncio.run(worker(args.url, paths, args.output))

if __name__ == "__main__":
    main()