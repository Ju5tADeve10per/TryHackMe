#!/usr/bin/env python3
"""
Given an XOR-encoded hex blob (repeated-key XOR with key length 5),
attempt to recover a plaintext flag that starts with "THM{" by:
  - deriving key[0..3] from "THM{" and the first 4 bytes of the blob
  - brute-forcing plausible candidates for the 5th plaintext char
  - decrypting the whole blob and checking for a sensible THM{...} result
"""

import sys
import string

KEYLEN = 5
PREFIX = b"THM{"            # assumed flag prefix
CAND5 = string.ascii_letters + string.digits + "_-{}"  # include braces in case

def fromhex_safe(h):
    h = h.strip()
    if h.startswith("0x") or h.startswith("0X"):
        h = h[2:]
    return bytes.fromhex(h)

def is_sensible_plain(p: bytes):
    # simple heuristics: printable ASCII (space..~), starts with THM{ and contains closing '}' later
    if not p.startswith(PREFIX):
        return False
    if b'}' not in p:
        return False
    # check printability (allow newline stripped)
    for b in p:
        if b < 32 or b > 126:
            return False
    return True

def main():
    try:
        hex_input = input().strip()
    except EOFError:
        print("No input", file=sys.stderr)
        return

    try:
        xored = fromhex_safe(hex_input)
    except Exception as e:
        print("Invalid hex:", e, file=sys.stderr)
        return

    if len(xored) < KEYLEN:
        print("Hex too short for keylen", KEYLEN, file=sys.stderr)
        return

    # derive key[0..3] from PREFIX
    key_bytes = [None] * KEYLEN
    for i in range(len(PREFIX)):
        key_bytes[i] = xored[i] ^ PREFIX[i]

    # brute force plaintext[4] candidates -> key[4], then decrypt full and test
    for ch in CAND5:
        pb4 = ord(ch)
        kb4 = xored[4] ^ pb4
        kb = key_bytes.copy()
        kb[4] = kb4
        # build repeated key and decrypt
        key_full = bytes(kb)
        plain = bytes([ xored[i] ^ key_full[i % KEYLEN] for i in range(len(xored)) ])
        if is_sensible_plain(plain):
            print("FOUND candidate key (hex):", key_full.hex())
            try:
                print("Key (ascii):", key_full.decode('ascii'))
            except:
                print("Key (ascii):", repr(key_full))
            print("Recovered plaintext:")
            print(plain.decode('ascii'))
            return

    print("No sensible plaintext found with the tested candidate set.")
    print("You can widen CAND5 (add more possible plaintext chars) and retry.")

if __name__ == "__main__":
    main()
