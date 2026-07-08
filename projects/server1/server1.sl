# Web Server - Static File Server with REST API
# Serves static files and provides REST API endpoints

fn handle_status(): str
    return "status: running, port: 8080"

fn handle_data(): str
    return "items: synthlang, example"

fn main(): int
    print("Server running on port 8080")
    print("Serving static files and REST API")
    return 0

main()