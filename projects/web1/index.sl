# Portfolio Website - Main Server Script
# Serves pages and handles contact form submissions

fn index(): str
    return "Welcome to SynthLang Portfolio!"

fn about(): str
    return "About SynthLang - A modern polyglot programming language."

fn contact(): str
    return "Contact form - Send your message!"

fn api_status(): str
    return "status: running, version: 1.1.0"

fn main(): int
    print("Starting portfolio server on http://localhost:8080")
    print("Routes: /, /about, /contact, /api/status")
    return 0

main()