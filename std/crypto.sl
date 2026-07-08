# High-performance crypto module (Rust backed)
@rust module "./src/rust/std/crypto" as crypto_native

fn hash_sha256(data):
    crypto_native.crypto_hash_sha256(data)

fn hash_sha512(data):
    crypto_native.crypto_hash_sha512(data)

fn generate_token(length): 
    # Use Python fallback for random generation
    @python module "secrets" as secrets
    secrets.token_hex(length)

fn random_bytes(length):
    crypto_native.random_bytes(length)

fn constant_time_compare(a, b):
    crypto_native.constant_time_compare(a, b)

fn hash(data):
    hash_sha256(data)