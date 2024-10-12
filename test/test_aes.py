from src.security import aes
import time


key128: bytes = aes.generate_key(128)
key192: bytes = aes.generate_key(192)
key256: bytes = aes.generate_key(256)


def tests(key: bytes):
    start = time.time()
    text: str = 'asihj'
    enc = aes.encrypt(key, text, 1024 * 10)
    dec = aes.decrypt(key, enc, 1024 * 10)

    #print(enc)
    #print(dec.decode())
    print(f'{(time.time() - start):02f}s')

tests(key128)
tests(key192)
tests(key256)