#!/usr/bin/env python3
"""
ns (nscan) - Simple Networkd Scanner with Optional Banner Grab

A simple TCP port scanner with optional banner grabbing to identify services and versions.
"""

import socket
import argparse
from concurrent.futures import ThreadPoolExecutor
import time
import sys
if sys.version_info < (3, 8):
    sys.exit("Please run with Python 3.8+")

# List of well-knwon ports (0 - 1023)
WELL_KNOWN_PORTS = list(range(0, 1024))

def grab_banner(ip: str, port: int, timeout: float = 0.5) -> str | None:
    """
    Attempt to grab a simple service banner from the given IP and port.

    Args:
        ip (str): Target IP address
        port (int): Target port number
        timeout (float): Socket timeout in seconds
    
    Returns:
        str | None: Banner text if retrieved, otherwise None
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))

        # Special handling for HTTP services: send a simple GET request
        if port in (80, 8080, 8000, 8008, 8888):
            try:
                request = f"GET / HTTP/1.0\r\nHost: {ip}\r\n\r\n"
                sock.sendall(request.encode('ascii', errors='ignore'))
            except Exception:
                pass
        # Receive up to 2048 bytes from the service
        data = sock.recv(2048)
        if not data:
            return None
        
        # Decode and clean up banner lines
        banner = data.decode('utf-8', errors='ignore').strip()
        lines = [line.strip() for line in banner.splitlines() if line.strip()]
        if not lines:
            return None
        
        # If HTTP server header exists, extract it
        for line in lines:
            if line.lower().startswith("server:"):
                return line.split(":", 1)[1].strip()
        
        # Otherwise, return first line (truncated if too long)
        banner = lines[0]
        if len(banner) > 200:
            banner = banner[:197] + "..."
        return banner
    except Exception:
        return None
    finally:
        if sock:
            try:
                sock.close()
            except Exception:
                pass

def scan_port(ip: str, port: int, get_service: bool = False, timeout: float = 0.5) -> tuple:
    """
    Scan a single TCP port to check if it is open, optionally grabbing its banner.

    Args:
        ip (str): Target IP address
        port (int): Port number to scan
        get_service (bool): Whether to retrieve service banner
        timeout (float): Socket timeout in seconds
    
    Returns:
        tuple: (port, is_open, service_name, banner)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))

        # Try to resolve the port to a standard service name
        try:
            service = socket.getservbyport(port, "tcp")
        except OSError:
            service = "unknown"
        
        banner = grab_banner(ip, port, timeout) if get_service else None
        return port, True, service, banner
    except Exception:
        return port, False, None, None
    finally:
        sock.close()

def scan_ports(ip: str, ports: list[int], get_service: bool = False) -> list[tuple]:
    """
    Scan multiple ports concurrently using a thread pool.

    Args:
        ip (str): Target IP address
        ports (list[int]): List of port numbers to scan
        get_service (bool): Whether to retrieve banners
    
    Returns:
        list[tuple]: List of scan results as (port, is_open, service, banner)
    """
    results = []
    # Use a ThreadPoolExecutor for concurrent scanning
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, ip, port, get_service) for port in ports]
        for future in futures:
            results.append(future.result())
    return results

def main() -> None:
    """
    Parse CLI arguments, perform port scanning, and display results.
    """
    parser = argparse.ArgumentParser(
        description="nscan (ns) - simple network scanner with optional banner grab"
    )
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument("--all", action="store_true", help="Scan all ports (0-65535)")
    parser.add_argument("--ports", help="Comma separated list of ports to scan")
    parser.add_argument(
        "--service",
        action="store_true",
        help="Grab banners to identify service/version"
    )
    args = parser.parse_args()

    # Determine ports to scan
    if args.all:
        ports = list(range(0, 65536))
    elif args.ports:
        ports = [int(p.strip()) for p in args.ports.split(",")]
    else:
        ports = WELL_KNOWN_PORTS
    
    # Start scan
    start_time = time.time()
    results = scan_ports(args.ip, ports, get_service=args.service)
    elapsed = time.time() - start_time

    # Separate open and closed ports
    open_ports = [r for r in results if r[1]]
    closed_count = len(results) - len(open_ports)

    # Header
    print(f"ns scan report for {args.ip}")
    print(f"Host is up ({elapsed:.2f}s latency).")
    print(f"Not shown: {closed_count} closed tcp ports (conn-refused)\n")

    # Display port table
    if args.service:
        print(f"{'PORT':<6} {'STATE':<8} {'SERVICE':<14} {'VERSION'}")
        for port, is_open, service, banner in sorted(open_ports):
            print(f"{port}/tcp {'open':<8} {service:<14} {banner if banner else ''}")
    else:
        print(f"{'PORT':<6} {'STATE':<6} {'SERVICE'}")
        for port, is_open, service, _ in sorted(open_ports):
            print(f"{port}/tcp {'open':<6} {service}")
    
    # Footer
    print(f"\nScan done: 1 IP address (1 host up) scanned in {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
