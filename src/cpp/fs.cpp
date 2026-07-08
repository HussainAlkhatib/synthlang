#include <string>
#include <vector>
#include <fstream>
#include <filesystem>
#include <nlohmann/json.hpp>

namespace fs {

std::string read(const std::string& path) {
    std::ifstream file(path);
    if (file.is_open()) {
        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        file.close();
        return content;
    }
    return "";
}

bool write(const std::string& path, const std::string& content) {
    std::ofstream file(path);
    if (file.is_open()) {
        file << content;
        file.close();
        return true;
    }
    return false;
}

std::string read_json(const std::string& path) {
    std::ifstream file(path);
    if (file.is_open()) {
        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        file.close();
        return content;
    }
    return "{}";
}

bool write_json(const std::string& path, const std::string& json_data) {
    std::ofstream file(path);
    if (file.is_open()) {
        file << json_data;
        file.close();
        return true;
    }
    return false;
}

bool exists(const std::string& path) {
    return std::filesystem::exists(path);
}

bool is_file(const std::string& path) {
    return std::filesystem::is_regular_file(path);
}

bool is_dir(const std::string& path) {
    return std::filesystem::is_directory(path);
}

std::string join_path(const std::string& a, const std::string& b) {
    return (std::filesystem::path(a) / b).string();
}

std::string get_parent(const std::string& path) {
    return std::filesystem::path(path).parent_path().string();
}

std::string get_name(const std::string& path) {
    return std::filesystem::path(path).filename().string();
}

std::vector<std::string> list_dir(const std::string& path) {
    std::vector<std::string> result;
    if (std::filesystem::exists(path) && std::filesystem::is_directory(path)) {
        for (const auto& entry : std::filesystem::directory_iterator(path)) {
            result.push_back(entry.path().string());
        }
    }
    return result;
}

} // namespace fs

extern "C" {
    const char* fs_read(const char* path) {
        static std::string result;
        result = fs::read(path);
        return result.c_str();
    }
    
    int fs_write(const char* path, const char* content) {
        return fs::write(path, content) ? 1 : 0;
    }
    
    int fs_exists(const char* path) {
        return fs::exists(path) ? 1 : 0;
    }
    
    int fs_is_file(const char* path) {
        return fs::is_file(path) ? 1 : 0;
    }
    
    int fs_is_dir(const char* path) {
        return fs::is_dir(path) ? 1 : 0;
    }
}