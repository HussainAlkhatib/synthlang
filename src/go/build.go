// +build ignore

package main

// Build script for cross-platform compilation of the Go shared library

import (
	"fmt"
	"os"
	"os/exec"
	"runtime"
)

func main() {
	output := getOutputName()

	cmd := exec.Command("go", "build", "-buildmode=c-shared", "-o", output, ".")
	cmd.Dir = "src/go"
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	fmt.Printf("Building Go shared library: %s\n", output)
	if err := cmd.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "Build failed: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Build successful: %s\n", output)

	dest := "src/synthlang/" + output
	copyFile(output, dest)
	fmt.Printf("Copied to: %s\n", dest)
}

func getOutputName() string {
	switch runtime.GOOS {
	case "windows":
		return "libgoffi.dll"
	case "darwin":
		return "libgoffi.dylib"
	default:
		return "libgoffi.so"
	}
}

func copyFile(src, dst string) error {
	input, err := os.ReadFile(src)
	if err != nil {
		return err
	}
	return os.WriteFile(dst, input, 0644)
}