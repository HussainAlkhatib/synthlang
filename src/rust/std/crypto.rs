use sha2::{Sha256, Sha512, Digest};

pub fn hash_sha256(data: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    format!("{:x}", hasher.finalize())
}

pub fn hash_sha512(data: &str) -> String {
    let mut hasher = Sha512::new();
    hasher.update(data);
    format!("{:x}", hasher.finalize())
}

pub fn random_bytes(len: usize) -> Vec<u8> {
    use rand::Rng;
    let mut rng = rand::thread_rng();
    (0..len).map(|_| rng.gen::<u8>()).collect()
}

pub fn constant_time_compare(a: &str, b: &str) -> bool {
    if a.len() != b.len() {
        return false;
    }
    a.bytes().zip(b.bytes()).map(|(a, b)| a ^ b).sum::<u8>() == 0
}

#[no_mangle]
pub extern "C" fn crypto_hash_sha256(data: *const i8) -> *const i8 {
    let input = unsafe { std::ffi::CStr::from_ptr(data).to_str().unwrap_or("") };
    let result = hash_sha256(input);
    // In real implementation, would need to manage memory properly
    Box::into_raw(Box::new(result)) as *const i8
}

#[no_mangle]
pub extern "C" fn crypto_hash_sha512(data: *const i8) -> *const i8 {
    let input = unsafe { std::ffi::CStr::from_ptr(data).to_str().unwrap_or("") };
    let result = hash_sha512(input);
    Box::into_raw(Box::new(result)) as *const i8
}