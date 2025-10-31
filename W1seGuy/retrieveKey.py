xored_text = input("Input xored-text: ")
key_parts = xored_text[0:4] + xored_text[-1]
print("Retrieved key_parts: ", key_parts)
flag_parts = "THM{}"
key = ""
for i in range(len(key_parts)):
    key += chr(ord(key_parts[i]) ^ ord(flag_parts[i]))
print("Key:", key)