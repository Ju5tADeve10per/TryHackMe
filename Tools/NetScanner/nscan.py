#!/usr/bin/env python3
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

WELL_KNOWN_PORTS = list(range(0, 1024))

# Scan a port
def scan_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect((ip, port))
        try:
            service = socket.getservbyport(port, "tcp")
        except OSError:
            service = "unknown"
        return port, True, service
    except:
        return port, False, None
    finally:
        sock.close()

# Scan multiple ports simultaneously
def scan_ports(ip, ports):
    results = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in ports]
        for future in futures:
            results.append(future.result())
    return results

# Handle CLI
def main():
    parser = argparse.ArgumentParser(description="nscan (ns) - simple network scanner")
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument("--all", action="store_true", help="Scan all ports (0-65535)")
    parser.add_argument("--ports", help="Comma separated list of ports to scan")
    args = parser.parse_args()

    if args.all:
        ports = list(range(0, 65536)) # why 65536, because of range?
    elif args.ports:
        ports = [int(p.strip()) for p in args.ports.split(",")]
    else:
        ports = WELL_KNOWN_PORTS
    
    start_time = time.time()
    results = scan_ports(args.ip, ports)
    end_time = time.time()
    elapsed = end_time - start_time

    open_ports = [r for r in results if r[1]]
    closed_count = len(results) - len(open_ports)

    # Header
    print(f"ns scan report for {args.ip}")
    print(f"Host is up ({elapsed:.2f}s latency).")
    print(f"Not shown: {closed_count} closed tcp ports (conn-refused)\n")

    # Port Table
    print(f"{'PORT':<8} {'STATE':<6} {'SERVICE'}")
    for port, is_open, service in sorted(open_ports):
        print(f"{port}/tcp {'open':<6} {service}")

    # Footer
    print(f"\nScan done: 1 IP address (1 host up) scanned in {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()