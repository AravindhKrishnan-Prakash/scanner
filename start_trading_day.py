#!/usr/bin/env python3
"""
One-click script to start your trading day
Generates token and starts the scanner automatically
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def main():
    print("=" * 60)
    print("🚀 STARTING TRADING DAY")
    print("=" * 60)
    
    # Step 1: Generate Upstox token
    print("\n📝 Step 1: Generating Upstox Access Token...")
    print("-" * 60)
    
    try:
        # Run token generator
        result = subprocess.run(
            [sys.executable, "get_upstox_token.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Token generated successfully!")
        else:
            print("❌ Token generation failed!")
            print(result.stderr)
            return
            
    except subprocess.TimeoutExpired:
        print("⏱️ Token generation timed out. Please complete manually.")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Start the scanner
    print("\n🔍 Step 2: Starting Live Scanner...")
    print("-" * 60)
    print("✅ Scanner is now running!")
    print("📧 You will receive email alerts when signals appear")
    print("🌐 Dashboard: http://127.0.0.1:8010")
    print("\n⚠️  Press Ctrl+C to stop the scanner")
    print("=" * 60)
    
    # Open dashboard in browser
    webbrowser.open("http://127.0.0.1:8010")
    
    # Start the scanner (this will block until Ctrl+C)
    try:
        subprocess.run([sys.executable, "dashboard_server.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 Scanner stopped. Trading day ended.")
        print("=" * 60)

if __name__ == "__main__":
    main()
