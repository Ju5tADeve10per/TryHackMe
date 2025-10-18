#!/usr/bin/env python3
import socket
import re
import time
import sys

HOST = "10.201.76.171"
PORT = 1337
KNOWN_FLAG = b"THM{thisisafakeflag}"
KEY_LEN = 5

def extract_hex(s):
    m = re.search(r"flag 1:\s*([0-9a-fA-F]+)", s)
    return m.group(1) if m else None

def recv_until(sock, patterns, timeout=6.0):
    """patterns: list of regex strings. return tuple(full_buf, matched_pattern_or_None)"""
    sock.settimeout(0.8)
    buf = ""
    start = time.time()
    while True:
        if time.time() - start > timeout:
            return buf, None
        try:
            chunk = sock.recv(4096)
            if not chunk:
                return buf, None
            s = chunk.decode(errors="ignore")
            buf += s
            for p in patterns:
                if re.search(p, buf):
                    return buf, p
        except socket.timeout:
            continue
        except Exception:
            return buf, None

def main():
    try:
        sock = socket.create_connection((HOST, PORT), timeout=5)
    except Exception as e:
        print("Connection error:", e)
        return

    with sock:
        # banner を受け取って hex が来るまで待つ
        buf, matched = recv_until(sock, [r"flag 1:\s*[0-9a-fA-F]+", r"What is the encryption key\?"], timeout=8.0)
        print("Initial receive:")
        print(buf)

        hexs = extract_hex(buf)
        if not hexs:
            print("Could not find hex in banner. Full banner above.")
            return

        try:
            data = bytes.fromhex(hexs)
        except Exception as e:
            print("Hex decode error:", e)
            return

        if len(data) < KEY_LEN:
            print("Received hex is shorter than expected.")
            return

        # key を既知平文から復元
        key_bytes = bytes([ data[i] ^ KNOWN_FLAG[i] for i in range(KEY_LEN) ])
        try:
            key = key_bytes.decode('ascii')
        except Exception:
            # 非表示文字が混ざってる場合の保険
            key = ''.join(chr(b) if 32 <= b < 127 else '?' for b in key_bytes)
        print("Derived key:", key)

        # 送信（同一接続内）
        sock.sendall((key + "\n").encode())

        # 送信後の応答を受け取る（複数チャンクに対応）
        out_buf = ""
        sock.settimeout(0.8)
        start = time.time()
        while True:
            # 総待ち時間を設ける（任意）
            if time.time() - start > 6.0:
                break
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                out_buf += chunk.decode(errors="ignore")
                if "Congrats" in out_buf or "Close but no cigar" in out_buf:
                    break
            except socket.timeout:
                continue
            except Exception:
                break

        print("Response:")
        print(out_buf)

if __name__ == "__main__":
    main()
