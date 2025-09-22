#!/usr/bin/env python3
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor

# Default well-known ports
WELL_KNOWN_PORTS = list(range(0, 1024))

# Scan Ports
def scan_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect((ip, port))
        return port, True
    except:
        return port, False
    finally:
        sock.close()

# Scan multiple ports simultaneously
def scan_port(ip, ports):
    results = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in ports]
        for future in futures:
            results.append(future.result())
    return results

# Handle CLI
def main():
    parser = argparse.ArgumentParser(description="ns - simple network scanner")
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument("--all", action="store_true", help="Scan all ports (0 - 65535)")
    parser.add_argument("--ports", help="Comma separated list of ports to scan")
    args = parser.parse_args()

    if args.all:
        ports = list(range(0, 65536))
    elif args.ports:
        ports = [int(p.strip()) for p in args.ports.split(",")]
    else:
        ports = WELL_KNOWN_PORTS
    
    print(f"Scanning {args.ip} ...")
    results = scan_ports(args.ip, ports)
    for port, is_open in results:
        status = "open" if is_open else "closed"
        print(f"Port {port}: {status}")

if __name__ == "__main__":
    main()