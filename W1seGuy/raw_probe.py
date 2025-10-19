#!/usr/bin/env python3
# raw_probe.py
# Connect, receive raw banner (repr), compute key from known fake flag, send it, then print raw response (repr).
import socket, re, sys

HOST = "10.201.69.39"
PORT = 1337
KNOWN_FAKE = b"THM{thisisafakeflag}"
KEYLEN = 5

def recv_all(sock, timeout=2.0):
    sock.settimeout(0.5)
    buf = b""
    import time
    t0 = time.time()
    while True:
        if time.time() - t0 > timeout:
            break
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
        except socket.timeout:
            continue
        except Exception:
            break
    return buf

with socket.create_connection((HOST, PORT), timeout=5) as s:
    banner = recv_all(s, timeout=2.0)
    print("BANNER (raw repr):")
    print(repr(banner))
    # try to extract hex bytes from banner
    m = re.search(br"flag 1:\s*([0-9a-fA-F]+)", banner)
    if not m:
        print("No hex found in banner.")
        sys.exit(1)
    hx = m.group(1).decode()
    print("HEX:", hx)
    xored = bytes.fromhex(hx)
    if len(xored) < KEYLEN:
        print("hex too short")
        sys.exit(1)
    key_bytes = bytes([ xored[i] ^ KNOWN_FAKE[i] for i in range(KEYLEN) ])
    try:
        key = key_bytes.decode('ascii')
    except:
        key = ''.join(chr(b) if 32<=b<127 else '?' for b in key_bytes)
    print("DERIVED KEY (ascii):", key, "  (hex:", key_bytes.hex(), ")")
    # send key + newline
    s.sendall((key + "\n").encode())
    resp = recv_all(s, timeout=2.0)
    print("RESPONSE (raw repr):")
    print(repr(resp))
    print("RESPONSE (decoded):")
    try:
        print(resp.decode(errors='replace'))
    except:
        print("<cannot decode>")
