xored_hextext = input("Input xored-hextext: ")
target = bytes.fromhex(xored_hextext[0:8] + xored[-2:])
key_seed = b"THM{}".hex()