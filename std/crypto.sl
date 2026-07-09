# High-performance crypto module (Rust backed)
@rust module "./src/rust/std/crypto" as crypto_native

fn hash_sha256(data: str):
    crypto_native.crypto_hash_sha256(data)

fn hash_sha512(data: str):
    crypto_native.crypto_hash_sha512(data)

fn hash_md5(data: str):
    crypto_native.crypto_hash_md5(data)

fn random_bytes(length: int):
    crypto_native.random_bytes(length)

fn random_int(min_val: int, max_val: int):
    @python module "random" as random
    random.randint(min_val, max_val)

fn constant_time_compare(a: str, b: str):
    crypto_native.constant_time_compare(a, b)

fn encrypt_aes256(data: str, key: str):
    crypto_native.encrypt_aes256(data, key)

fn decrypt_aes256(encrypted: str, key: str):
    crypto_native.decrypt_aes256(encrypted, key)

fn sign(data: str, private_key: str):
    crypto_native.sign(data, private_key)

fn verify(data: str, signature: str, public_key: str):
    crypto_native.verify(data, signature, public_key)

fn hash(data: str):
    hash_sha256(data)