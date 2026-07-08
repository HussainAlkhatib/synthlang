@python module "hashlib" as hashlib
@python module "secrets" as secrets

fn hash_sha256(data):
    let h = hashlib.sha256(data.encode())
    return h.hexdigest()

fn hash_md5(data):
    let h = hashlib.md5(data.encode())
    return h.hexdigest()

fn hash_sha1(data):
    let h = hashlib.sha1(data.encode())
    return h.hexdigest()

fn generate_token(length): 
    return secrets.token_hex(length)

fn random_int(min_val, max_val): 
    return secrets.randbelow(max_val - min_val + 1) + min_val