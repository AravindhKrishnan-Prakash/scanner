"""
Upstox Token Generator
Automates the process of getting a fresh access token daily
"""
import os
import webbrowser
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Load environment variables
def load_env_file(path: Path = Path(".env")) -> dict:
    env_vars = {}
    if not path.exists():
        return env_vars
    
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        env_vars[key] = value
        os.environ[key] = value
    
    return env_vars

print("=" * 70)
print("UPSTOX ACCESS TOKEN GENERATOR")
print("=" * 70)

# Load .env file
env_vars = load_env_file()

# Step 1: Get API credentials from .env or prompt
print("\n📋 Step 1: Loading API credentials from .env file")
print("-" * 70)

api_key = env_vars.get("UPSTOX_API_KEY", "").strip()
api_secret = env_vars.get("UPSTOX_API_SECRET", "").strip()

if api_key and api_secret:
    print(f"✓ API Key found: {api_key[:10]}...")
    print(f"✓ API Secret found: {'*' * 20}")
else:
    print("⚠ API credentials not found in .env file")
    print("\nPlease add to your .env file:")
    print("UPSTOX_API_KEY=your_api_key_here")
    print("UPSTOX_API_SECRET=your_api_secret_here")
    print("\nOr enter them now:")
    print("-" * 70)
    api_key = input("Enter your API Key (Client ID): ").strip()
    api_secret = input("Enter your API Secret: ").strip()

if not api_key or not api_secret:
    print("\n❌ Error: API Key and Secret are required!")
    print("Get them from: https://account.upstox.com/developer/apps")
    exit(1)

# Step 2: Generate authorization URL
redirect_uri = "http://localhost:8080"
auth_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={api_key}&redirect_uri={redirect_uri}"

print("\n" + "=" * 70)
print("📱 Step 2: Authorize the application")
print("=" * 70)
print("\nOpening browser for authorization...")
print("If browser doesn't open, copy this URL:")
print(f"\n{auth_url}\n")

# Open browser
try:
    webbrowser.open(auth_url)
except:
    pass

print("-" * 70)
print("After you authorize:")
print("1. You'll be redirected to: http://localhost:8080?code=XXXXX")
print("2. The page won't load (that's normal)")
print("3. Copy the FULL URL from your browser address bar")
print("-" * 70)

# Step 3: Get authorization code
redirect_url = input("\nPaste the full redirect URL here: ").strip()

if not redirect_url:
    print("\n❌ Error: Redirect URL is required!")
    exit(1)

# Parse the authorization code
try:
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    auth_code = query_params.get('code', [None])[0]
    
    if not auth_code:
        print("\n❌ Error: Could not find authorization code in URL!")
        print("Make sure you copied the complete URL with ?code=...")
        exit(1)
    
    print(f"\n✓ Authorization code extracted: {auth_code[:20]}...")
    
except Exception as e:
    print(f"\n❌ Error parsing URL: {e}")
    exit(1)

# Step 4: Exchange code for access token
print("\n" + "=" * 70)
print("🔄 Step 3: Exchanging code for access token...")
print("=" * 70)

token_url = "https://api.upstox.com/v2/login/authorization/token"
token_data = {
    "code": auth_code,
    "client_id": api_key,
    "client_secret": api_secret,
    "redirect_uri": redirect_uri,
    "grant_type": "authorization_code"
}

try:
    response = requests.post(token_url, data=token_data)
    response.raise_for_status()
    
    token_response = response.json()
    access_token = token_response.get("access_token")
    
    if not access_token:
        print("\n❌ Error: No access token in response!")
        print(f"Response: {token_response}")
        exit(1)
    
    print("\n✅ SUCCESS! Access token generated!")
    print("=" * 70)
    
    # Step 5: Update .env file
    print("\n📝 Step 4: Updating .env file...")
    
    try:
        # Read current .env
        with open(".env", "r") as f:
            lines = f.readlines()
        
        # Update token line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("UPSTOX_ACCESS_TOKEN="):
                lines[i] = f"UPSTOX_ACCESS_TOKEN={access_token}\n"
                updated = True
                break
        
        # If not found, add it
        if not updated:
            lines.insert(0, f"UPSTOX_ACCESS_TOKEN={access_token}\n")
        
        # Write back
        with open(".env", "w") as f:
            f.writelines(lines)
        
        print("✓ .env file updated successfully!")
        
    except Exception as e:
        print(f"\n⚠ Could not update .env file automatically: {e}")
        print("\nManually add this to your .env file:")
        print(f"\nUPSTOX_ACCESS_TOKEN={access_token}\n")
    
    print("\n" + "=" * 70)
    print("🎉 ALL DONE!")
    print("=" * 70)
    print("\nYour access token is valid until end of trading day (6 PM IST)")
    print("\nNext steps:")
    print("1. Restart your scanner: .venv\\Scripts\\python dashboard_server.py")
    print("2. Open dashboard: http://127.0.0.1:8010")
    print("3. Tomorrow, run this script again to get a fresh token")
    print("\n💡 Tip: Run this script every morning before market opens!")
    print("=" * 70)
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ Error getting access token: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
    exit(1)
