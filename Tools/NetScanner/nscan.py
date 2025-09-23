#!/usr/bin/env python3
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

WELL_KNOWN_PORTS = list(range(0, 1024))

def grab_banner(ip, port, timeout=0.5):
    """Try to grab a simple banner from a service."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))

        # Special handling for HTTP
        if port in (80, 8080, 8000, 8008, 8888):
            try:
                req = f"GET / HTTP/1.0\r\nHost: {ip}\r\n\r\n"
                sock.sendall(req.encode('ascii', errors='ignore'))
            except:
                pass
        
        data = sock.recv(2048) # what's this?
        sock.close()

        if not data:
            return None

        banner = data.decode('utf-8', errors='ignore').strip()
        lines = [line.strip() for line in banner.splitlines() if line.strip()]
        if not lines:
            return None
        
        # Extract HTTP server header if possible
        if any("server:" in line.lower() for line in lines):
            for line in lines:
                if line.lower().startswith("server:"):
                    return line.split(":", 1)[1].strip()
        
        # Otherwise just return first line
        banner = lines[0]
        if len(banner) > 200:
            banner = banner[:197] + "..."
        return banner
    
    except:
        return None
    finally:
        try:
            sock.close()
        except:
            pass

def scan_port(ip, port, timeout=0.5):
    """Scan a single port and optionally grab a banner."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
        try:
            service = socket.getservbyport(port, "tcp")
        except OSError:
            service = "unknown"
        
        banner = grab_banner(ip, port, timeout)
        return port, True, service, banner
    except:
        return port, False, None, None
    finally:
        sock.close()

def scan_ports(ip, ports):
    results = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in ports]
        for future in futures:
            results.append(future.result())
    return results

def main():
    parser = argparse.ArgumentParser(description="nscan (ns) - simple network scanner with banner grab")
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument("--all", action="store_true", help="Scan all ports (0-65535)")
    parser.add_argument("--ports", help="Comma separated list of ports to scan")
    parser.add_argument("--service", action="store_true", help="Grab banners to identify service/version")
    args = parser.parse_args()

    if args.all:
        ports = list(range(0, 65536))
    elif args.ports:
        ports = [int(p.strip()) for p in args.ports.split(",")]
    else:
        ports = WELL_KNOWN_PORTS
    
    start_time = time.time()
    results = scan_ports(args.ip, ports, get_service=args.service)
    end_time = time.time()
    elapsed = end_time - start_time

    open_ports = [r for r in results if r[1]]
    closed_count = len(results) - len(open_ports)

    # Header
    print(f"ns scan report for {args.ip}")
    print(f"Host is up ({elapsed:.2f}s latency).")
    print(f"Not shown: {closed_count} closed tcp ports (conn-refused)\n")

    # Port Table
    if args.service:
        print(f"{'PORT':<8} {'STATE':<6} {'SERVICE':<12} {'VERSION'}")
        for port, is_open, service, banner in sorted(open_ports):
            print(f"{port}/tcp {'open':<6} {service:<12} {banner if banner else ''}")
    else:
        print(f"{'PORT':<8} {'STATE':<6} {'SERVICE'}")
        for port, is_open, service, _ in sorted(open_ports):
            print(f"{port}/tcp {'open':<6} {service}")
    
    # Footer
    print(f"\nScan done: 1 IP address (1 host up) scanned in {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()