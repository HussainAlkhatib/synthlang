# Web Server example
# Using @web annotation for web services

@web
fn index(): str
    return "Welcome to SynthLang Web!"

@web
fn api_users(): list
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]

fn main(): int
    print("Starting web server on http://localhost:8080")
    return 0