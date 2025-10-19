#!/usr/bin/env python3
"""
Retrieve the XOR key from a hex-encoded string using a known plaintext.
Input: Paste the hex string when prompted.
Output: Prints the derived key (ASCII).
"""

KNOWN_FLAG = b"THM{thisisafakeflag}"
KEY_LEN = 5

def main():
    hex_input = input("Paste hex: ").strip()
    data = bytes.fromhex(hex_input)
    key_bytes = bytes([data[i] ^ KNOWN_FLAG[i] for i in range(KEY_LEN)])
    print(key_bytes.decode())

if __name__ == "__main__":
    main()