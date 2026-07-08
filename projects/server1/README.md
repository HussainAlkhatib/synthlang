# Web Server - Static File Server with REST API

A simple HTTP server that serves static files and provides a REST API. (v1.1.0)

## Description

This server demonstrates SynthLang's HTTP capabilities using FFI to C libraries or built-in support.

## How to Run

```bash
slang run server1/server1.sl
```

The server will start and listen on port 8080.

## Features

- Serves static files from `public/` directory
- REST API endpoints for JSON data
- FFI integration with C HTTP libraries (libmicrohttpd)

## API Endpoints

- `GET /` - Home page
- `GET /api/status` - Server status JSON
- `GET /api/data` - Sample data endpoint