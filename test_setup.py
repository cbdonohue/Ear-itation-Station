#!/usr/bin/env python3
"""
Test script to verify the ASMR Video Generator setup
"""

import os
import sys
import importlib.util
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'aiofiles',
        'requests',
        'openai',
        'python_dotenv'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'python_dotenv':
                import dotenv
            else:
                __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required modules are available")
    return True

def test_files():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'main.py',
        'cli.py',
        'ai_video_generator.py',
        'requirements.txt',
        'amplify.yml',
        'runtime.txt',
        'Procfile',
        'env.example'
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present")
    return True

def test_directories():
    """Test that required directories exist or can be created"""
    print("\n📂 Testing directories...")
    
    required_dirs = [
        'generated_videos',
        'video_metadata'
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✅ {dir_name}/ (exists)")
        else:
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"  ✅ {dir_name}/ (created)")
            except Exception as e:
                print(f"  ❌ {dir_name}/ (failed to create: {e})")
                return False
    
    print("✅ All required directories are ready")
    return True

def test_environment():
    """Test environment variable configuration"""
    print("\n🔧 Testing environment configuration...")
    
    required_env_vars = [
        'OPENAI_API_KEY',
        'WAVESPEED_API_KEY',
        'FAL_API_KEY'
    ]
    
    # Load .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("  📄 Loaded .env file")
    else:
        print("  ⚠️  No .env file found (using system environment variables)")
    
    missing_vars = []
    
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            # Show first 8 characters and mask the rest
            masked_value = value[:8] + '*' * (len(value) - 8) if len(value) > 8 else value[:4] + '*' * (len(value) - 4)
            print(f"  ✅ {var} = {masked_value}")
        else:
            print(f"  ❌ {var} (not set)")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Copy env.example to .env and fill in your API keys")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_syntax():
    """Test that Python files have valid syntax"""
    print("\n🐍 Testing Python syntax...")
    
    python_files = [
        'main.py',
        'cli.py',
        'ai_video_generator.py'
    ]
    
    for file in python_files:
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"  ✅ {file}")
        except SyntaxError as e:
            print(f"  ❌ {file} (syntax error: {e})")
            return False
        except Exception as e:
            print(f"  ❌ {file} (error: {e})")
            return False
    
    print("✅ All Python files have valid syntax")
    return True

def main():
    """Run all tests"""
    print("🧪 ASMR Video Generator Setup Test")
    print("=" * 40)
    
    tests = [
        test_files,
        test_directories,
        test_imports,
        test_syntax,
        test_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Start the server: python cli.py server")
        print("2. Generate a video: python cli.py generate --wait")
        print("3. View API docs: http://localhost:8000/docs")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
