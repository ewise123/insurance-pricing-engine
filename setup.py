#!/usr/bin/env python3
"""
Insurance Pricing Engine - Setup Script
Checks dependencies and provides installation instructions
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependency(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} installed")
        return True
    except ImportError:
        print(f"❌ {package_name} not installed")
        return False

def main():
    print("=" * 60)
    print("Insurance Pricing Engine - Setup Check")
    print("=" * 60)
    print()
    
    # Check Python version
    print("Checking Python version...")
    if not check_python_version():
        print("\n⚠️  Please upgrade Python to 3.10 or higher")
        sys.exit(1)
    print()
    
    # Check required packages
    print("Checking dependencies...")
    dependencies = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('python-multipart', 'multipart')
    ]
    
    missing = []
    for package, import_name in dependencies:
        if not check_dependency(package, import_name):
            missing.append(package)
    
    print()
    
    if missing:
        print("=" * 60)
        print("⚠️  Missing Dependencies")
        print("=" * 60)
        print("\nRun this command to install:")
        print(f"\npip install {' '.join(missing)}")
        print("\nOr install all at once:")
        print("\npip install fastapi uvicorn pandas numpy python-multipart")
        print()
        return False
    
    # Check data files
    print("Checking data files...")
    data_files = [
        'historical_customers.csv',
        'new_customers.csv'
    ]
    
    for filename in data_files:
        if os.path.exists(filename):
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            print(f"✅ {filename} ({size_mb:.1f} MB)")
        else:
            print(f"❌ {filename} missing")
    
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nYou're ready to run the system!")
    print("\n📋 Next Steps:")
    print("\n1. Quick Demo:")
    print("   python demo_script.py")
    print("\n2. Start Full System:")
    print("   python backend_api.py")
    print("   Then open frontend.html in your browser")
    print("\n3. Read Documentation:")
    print("   - QUICK_START.md for 2-minute setup")
    print("   - README.md for full documentation")
    print("   - ARCHITECTURE.md for technical details")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
