#!/bin/bash
# SynthLang Cross-Platform Installer for Linux/macOS

set -e

INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"
CACHE_DIR="${CACHE_DIR:-$HOME/.slang/slangs}"
COLORS_DIR="/usr/local/lib/slang/colors"

detect_platform() {
    case "$(uname -s)" in
        Linux*)     PLATFORM="linux";;
        Darwin*)    PLATFORM="macos";;
        *)          echo "Unsupported platform: $(uname -s)"; exit 1;;
    esac
    echo "Detected platform: $PLATFORM"
}

download_binary() {
    BINARY_URL="https://github.com/synthlang/synthlang/releases/latest/download/slang-$PLATFORM-x86_64"
    TEMP_FILE="/tmp/slang-binary"
    
    echo "Downloading SynthLang binary..."
    if command -v curl &> /dev/null; then
        curl -L -o "$TEMP_FILE" "$BINARY_URL" || wget -O "$TEMP_FILE" "$BINARY_URL"
    else
        wget -O "$TEMP_FILE" "$BINARY_URL"
    fi
}

install_binary() {
    mkdir -p "$INSTALL_PREFIX/lib/slang/bin"
    mkdir -p "$INSTALL_PREFIX/lib/slang/lib/core"
    mkdir -p "$INSTALL_PREFIX/lib/slang/lib/stdlib"
    mkdir -p "$INSTALL_PREFIX/lib/slang/lib/go"
    mkdir -p "$CACHE_DIR/python"
    mkdir -p "$CACHE_DIR/node"
    
    mv "$TEMP_FILE" "$INSTALL_PREFIX/lib/slang/bin/slang"
    chmod +x "$INSTALL_PREFIX/lib/slang/bin/slang"
    
    ln -sf "$INSTALL_PREFIX/lib/slang/bin/slang" "$INSTALL_PREFIX/bin/slang"
    
    # Copy Go FFI library if built
    if [ -f "src/synthlang/libgoffi.so" ]; then
        cp "src/synthlang/libgoffi.so" "$INSTALL_PREFIX/lib/slang/lib/go/"
    elif [ -f "src/synthlang/libgoffi.dylib" ]; then
        cp "src/synthlang/libgoffi.dylib" "$INSTALL_PREFIX/lib/slang/lib/go/"
    fi
    
    echo "$VERSION" > "$INSTALL_PREFIX/lib/slang/version.txt"
    
    echo "Installed to $INSTALL_PREFIX/lib/slang"
}

install_icon() {
    # Install .sl file icon
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [ "$PLATFORM" = "linux" ]; then
        # Linux - XDG icon registration
        if command -v xdg-icon-resource &> /dev/null; then
            for size in 16 22 32 48 64 128 256; do
                ICON_SRC="$SCRIPT_DIR/assets/icon.png"
                if [ -f "$ICON_SRC" ]; then
                    xdg-icon-resource install --size $size "$ICON_SRC" application-x-synthlang 2>/dev/null || true
                fi
            done
        fi
        # Register MIME type
        if command -v xdg-mime &> /dev/null && [ -f "$SCRIPT_DIR/colors/synthlang.xml" ]; then
            xdg-mime install "$SCRIPT_DIR/colors/synthlang.xml" 2>/dev/null || true
        fi
    elif [ "$PLATFORM" = "macos" ]; then
        # macOS - Copy icon to resources
        if command -v fileicon &> /dev/null && [ -f "$SCRIPT_DIR/assets/icon.png" ]; then
            fileicon set /usr/local/bin/slang "$SCRIPT_DIR/assets/icon.png" 2>/dev/null || true
        fi
    fi
}

install_colors() {
    echo "Installing syntax highlighting..."
    mkdir -p "$COLORS_DIR"
    
    # Copy all color definitions
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -d "$SCRIPT_DIR/colors" ]; then
        cp -r "$SCRIPT_DIR/colors"/* "$COLORS_DIR/"
    fi
    
    # Install icon
    install_icon
    
    # VS Code
    if command -v code &> /dev/null; then
        echo "Installing VS Code extension..."
        code --install-extension "$COLORS_DIR/vscode" 2>/dev/null || true
    fi
    
    # Vim
    if [ -d "$HOME/.vim" ]; then
        mkdir -p "$HOME/.vim/syntax"
        mkdir -p "$HOME/.vim/ftdetect"
        cp "$COLORS_DIR/vim/syntax/synthlang.vim" "$HOME/.vim/syntax/" 2>/dev/null || true
        cp "$COLORS_DIR/vim/ftdetect/synthlang.vim" "$HOME/.vim/ftdetect/" 2>/dev/null || true
        echo "Installed Vim syntax highlighting"
    fi
    
    # Neovim
    if [ -d "$HOME/.config/nvim" ]; then
        mkdir -p "$HOME/.config/nvim/syntax"
        mkdir -p "$HOME/.config/nvim/ftdetect"
        cp "$COLORS_DIR/neovim/syntax/synthlang.vim" "$HOME/.config/nvim/syntax/" 2>/dev/null || true
        cp "$COLORS_DIR/neovim/ftdetect/synthlang.vim" "$HOME/.config/nvim/ftdetect/" 2>/dev/null || true
        echo "Installed Neovim syntax highlighting"
    fi
    
    # Sublime Text
    if [ -d "$HOME/.config/sublime-text-3/Packages/User" ]; then
        cp "$COLORS_DIR/sublime/synthlang.sublime-syntax" "$HOME/.config/sublime-text-3/Packages/User/" 2>/dev/null || true
        echo "Installed Sublime Text syntax highlighting"
    fi
    
    # Emacs
    if [ -d "$HOME/.emacs.d" ]; then
        cp "$COLORS_DIR/emacs/synthlang-mode.el" "$HOME/.emacs.d/" 2>/dev/null || true
        if [ -f "$HOME/.emacs.d/init.el" ]; then
            grep -q "synthlang-mode" "$HOME/.emacs.d/init.el" || echo "(require 'synthlang-mode)" >> "$HOME/.emacs.d/init.el"
        fi
        echo "Installed Emacs syntax highlighting"
    fi
    
    # Antigravity IDE (VS Code fork)
    ANTIGRAVITY_EXT_DIR="$HOME/.antigravity-ide/extensions"
    if [ -d "$ANTIGRAVITY_EXT_DIR" ] || [ "$PLATFORM" = "linux" ]; then
        mkdir -p "$ANTIGRAVITY_EXT_DIR"
        cp -r "$COLORS_DIR/antigravity" "$ANTIGRAVITY_EXT_DIR/synthlang-1.0.0"
        echo "Installed Antigravity IDE syntax highlighting"
    fi
    
    echo "Syntax highlighting available at $COLORS_DIR"
}

create_user_paths() {
    mkdir -p "$HOME/.slang"
    mkdir -p "$CACHE_DIR/python"
    mkdir -p "$CACHE_DIR/node"
    
    if [[ ":$PATH:" != *":$INSTALL_PREFIX/bin:"* ]]; then
        echo "Adding $INSTALL_PREFIX/bin to PATH..."
        echo "export PATH=\"\$PATH:$INSTALL_PREFIX/bin\"" >> "$HOME/.bashrc"
        echo "export PATH=\"\$PATH:$INSTALL_PREFIX/bin\"" >> "$HOME/.zshrc" 2>/dev/null || true
    fi
    
    echo "export SLANG_SLANGSPATH=\"$CACHE_DIR\"" >> "$HOME/.bashrc"
    echo "export PYTHONPATH=\"\$PYTHONPATH:$CACHE_DIR/python\"" >> "$HOME/.bashrc"
    echo "export NODE_PATH=\"$CACHE_DIR/node\"" >> "$HOME/.bashrc"
}

main() {
    VERSION="1.0.0"
    detect_platform
    download_binary
    install_binary
    install_colors
    create_user_paths
    
    echo "SynthLang $VERSION installed successfully!"
    echo "Run 'slang --version' to verify installation."
}

main "$@"