import requests
import base64
import sys

# Your one-time-use Setup Token from the SimpleFIN website
# REPLACE THE LINE BELOW with the token you copied from SimpleFIN.
# This script is meant to be run once to get your permanent ACCESS URL.
SETUP_TOKEN = "REPLACE_WITH_YOUR_BASE64_SETUP_TOKEN" 

if SETUP_TOKEN == "REPLACE_WITH_YOUR_BASE64_SETUP_TOKEN":
    print("ERROR: Please update the SETUP_TOKEN variable in this script with your SimpleFIN setup token.")
    sys.exit(1)

# 1. Decode the Setup Token to get the "claim" URL
try:
    claim_url_bytes = base64.urlsafe_b64decode(SETUP_TOKEN)
    claim_url = claim_url_bytes.decode('utf-8')
except Exception as e:
    print(f"Error decoding setup token: {e}")
    sys.exit(1)

# 2. Make a POST request to the claim URL to get the Access URL
try:
    # Use 'Content-Length': '0' to signal an empty body in the POST request
    response = requests.post(claim_url, headers={'Content-Length': '0'})
    response.raise_for_status() # Check for errors
    
    # This is your final Access URL
    access_url = response.text.strip()
    
    print("Success! Your SimpleFIN Access URL is:")
    print("---------------------------------------------------------------------------------------------------------")
    print(access_url)
    print("---------------------------------------------------------------------------------------------------------")
    print("\nACTION REQUIRED: Copy this entire URL and paste it as the value for SIMPLEFIN_ACCESS_URL in your CONFIG.env file.")
    print("NOTE: The Setup Token used in this script is now invalid. You can delete this script once the URL is saved.")
    
except requests.exceptions.RequestException as e:
    print(f"Error exchanging the token: Could not reach SimpleFIN bridge.")
    print(f"Details: {e}")
