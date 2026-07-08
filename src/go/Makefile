.PHONY: build clean test

# Detect OS
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)

ifeq ($(UNAME_S),Windows)
	LIB_EXT = dll
	LIB_NAME = libgoffi.dll
else
	ifeq ($(UNAME_S),Darwin)
		LIB_EXT = dylib
		LIB_NAME = libgoffi.dylib
	else
		LIB_EXT = so
		LIB_NAME = libgoffi.so
	endif
endif

# Build the shared library
build:
ifeq ($(UNAME_S),Windows)
	go build -buildmode=c-shared -o $(LIB_NAME) .
else
	go build -buildmode=c-shared -o $(LIB_NAME) .
endif
	@echo "Built $(LIB_NAME)"

# Copy to synthlang directory
install: build
	cp $(LIB_NAME) ../synthlang/
	@echo "Installed $(LIB_NAME) to src/synthlang/"

# Clean build artifacts
clean:
	rm -f $(LIB_NAME) *.h

# Run tests
test:
	go test -v ./...

# Run benchmarks
bench:
	go test -bench=. -benchmem ./...