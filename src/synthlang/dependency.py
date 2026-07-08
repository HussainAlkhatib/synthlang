"""SynthLang Dependency Manager - slangs.json parsing and resolution."""
import json
import os
import subprocess
import sys
import platform
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import re


def get_slangs_cache_path() -> Path:
    system = platform.system()
    if system == "Windows":
        cache_base = Path(os.environ.get("PROGRAMFILES", "C:\\")) / "SynthLang" / "lib" / "slangs"
        return cache_base
    else:
        return Path.home() / ".slang" / "slangs"


@dataclass
class Dependency:
    name: str
    version: str
    source: str  # 'pip' or 'npm'

    def __repr__(self):
        return f"{self.name}@{self.version} ({self.source})"


@dataclass
class Manifest:
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    date: str = ""
    synthlang_version: str = ">=1.0.0"
    dependencies: Dict[str, Dict[str, str]] = field(default_factory=dict)
    dev_dependencies: Dict[str, Dict[str, str]] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "date": self.date,
            "synthlang_version": self.synthlang_version,
            "dependencies": self.dependencies,
            "dev_dependencies": self.dev_dependencies,
            "scripts": self.scripts,
            "metadata": self.metadata,
        }


class DependencyManager:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.manifest_path = self.project_dir / "slangs.json"
        self.lock_path = self.project_dir / "slangs.lock"
        self.manifest: Optional[Manifest] = None
        self.lock_data: Dict[str, Any] = {}

    def load_manifest(self) -> Manifest:
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"slangs.json not found in {self.project_dir}")
        with open(self.manifest_path, 'r') as f:
            data = json.load(f)
        self.manifest = Manifest(
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            date=data.get("date", ""),
            synthlang_version=data.get("synthlang_version", ">=1.0.0"),
            dependencies=data.get("dependencies", {}),
            dev_dependencies=data.get("dev_dependencies", {}),
            scripts=data.get("scripts", {}),
            metadata=data.get("metadata", {}),
        )
        return self.manifest

    def load_lock(self) -> Dict[str, Any]:
        if self.lock_path.exists():
            with open(self.lock_path, 'r') as f:
                self.lock_data = json.load(f)
        return self.lock_data

    def create_default_manifest(self, project_name: str) -> Manifest:
        from datetime import datetime
        self.manifest = Manifest(
            name=project_name,
            version="1.0.0",
            description=f"A SynthLang project",
            author="",
            date=datetime.now().strftime("%Y-%m-%d"),
            synthlang_version=">=1.0.0",
            dependencies={"pip": {}, "npm": {}},
            dev_dependencies={"pip": {}, "npm": {}},
            scripts={
                "start": "slang run main.sl",
                "build": "slang build",
                "test": "slang test"
            },
            metadata={"repository": "", "license": "MIT"},
        )
        return self.manifest

    def save_manifest(self):
        if self.manifest:
            with open(self.manifest_path, 'w') as f:
                json.dump(self.manifest.to_dict(), f, indent=2)

    def save_lock(self, lock_data: Dict[str, Any]):
        with open(self.lock_path, 'w') as f:
            json.dump(lock_data, f, indent=2)

    def install_pip_package(self, name: str, version: str = "", global_install: bool = False) -> bool:
        spec = f"{name}"
        if version:
            spec = f"{name}{self._parse_version_spec(version)}"
        try:
            if global_install:
                cache_path = get_slangs_cache_path() / "python"
                os.makedirs(cache_path, exist_ok=True)
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--target", str(cache_path), spec],
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", spec],
                    capture_output=True,
                    text=True
                )
            return result.returncode == 0
        except Exception as e:
            print(f"Error installing {name}: {e}")
            return False

    def install_npm_package(self, name: str, version: str = "", global_install: bool = False) -> bool:
        spec = f"{name}"
        if version:
            spec = f"{name}@{self._parse_version_spec(version)}"
        try:
            if global_install:
                cache_path = get_slangs_cache_path() / "node"
                os.makedirs(cache_path, exist_ok=True)
                result = subprocess.run(
                    ["npm", "install", spec, "--prefix", str(cache_path)],
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ["npm", "install", spec],
                    capture_output=True,
                    text=True,
                    cwd=self.project_dir
                )
            return result.returncode == 0
        except Exception as e:
            print(f"Error installing {name}: {e}")
            return False

    def install_all(self, use_lock: bool = True, global_install: bool = False) -> bool:
        if use_lock and self.lock_data:
            return self._install_from_lock(global_install=global_install)
        if not self.manifest:
            self.load_manifest()
        
        lock_data = {"version": "1.0", "dependencies": {}}
        
        for name, version in self.manifest.dependencies.get("pip", {}).items():
            if self.install_pip_package(name, version, global_install):
                lock_data["dependencies"][name] = {"pip": version}
        
        for name, version in self.manifest.dependencies.get("npm", {}).items():
            if self.install_npm_package(name, version, global_install):
                lock_data["dependencies"][name] = {"npm": version}
        
        self.save_lock(lock_data)
        return True

    def _install_from_lock(self, global_install: bool = False) -> bool:
        for name, versions in self.lock_data.get("dependencies", {}).items():
            if "pip" in versions:
                self.install_pip_package(name, versions["pip"], global_install)
            if "npm" in versions:
                self.install_npm_package(name, versions["npm"], global_install)
        return True

    def _parse_version_spec(self, version: str) -> str:
        if version.startswith("^") or version.startswith("~"):
            return f"=={version[1:]}"
        elif version.startswith(">="):
            return version
        elif version.startswith(">"):
            return version
        elif version.startswith("<="):
            return version
        return f"=={version}"

    def list_installed(self) -> List[Dependency]:
        deps = []
        for name, versions in self.manifest.dependencies.get("pip", {}).items():
            deps.append(Dependency(name, versions, "pip"))
        for name, versions in self.manifest.dependencies.get("npm", {}).items():
            deps.append(Dependency(name, versions, "npm"))
        return deps


def init_project(project_name: str, target_dir: Optional[str] = None):
    target = Path(target_dir) if target_dir else Path(".") / project_name
    target.mkdir(parents=True, exist_ok=True)
    
    dm = DependencyManager(target)
    dm.create_default_manifest(project_name)
    
    main_sl = '''# Main entry point
fn main(): void
    print("Hello from SynthLang!")
'''
    with open(target / "main.sl", 'w') as f:
        f.write(main_sl)
    
    dm.save_manifest()
    print(f"Created new SynthLang project: {target}")


def init_manifest(target_dir: str = "."):
    dm = DependencyManager(target_dir)
    dm.create_default_manifest(Path(target_dir).name)
    dm.save_manifest()
    print(f"Created slangs.json in {target_dir}")


if __name__ == '__main__':
    init_project("test_project")