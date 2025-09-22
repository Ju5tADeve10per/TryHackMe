#!/usr/bin/env python3
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor

WELL_KNOWN_PORTS = list(range(0, 1024))

# Scan a port
def scan_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect((ip, port))
        try:
            service = socket.getservbyport(port, "tcp") # why tcp?
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
    parser = argparse.ArgumentParser(description="ns - simple network scanner")
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument("--all", action="store_true", help="Scan all ports (0-65535)")
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

    print(f"\nOpen ports on {args.ip}:")
    for port, is_open, service in results:
        if is_open:
            print(f"{port}: {service} (tcp)")
            
if __name__ == "__main__":
    main()