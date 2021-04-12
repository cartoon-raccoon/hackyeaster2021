from hashlib import sha256

for i in range(10000000, 99999999):
    word = f"{i} hash browns".encode('ascii')
    hashedword = sha256(word).hexdigest()

    print(hashedword, word)
