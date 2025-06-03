import csv
import requests

# API endpoint for California ZIP codes
url = "https://unitedstateszipcodes.org/api/v1/zip-codes/state/CA?api_key=YOUR_API_KEY"  # Replace YOUR_API_KEY

try:
    # Make the API request
    response = requests.get(url)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

    # Parse the JSON response
    data = response.json()

    # Extract ZIP codes
    ca_zip_codes = [result["zip_code"] for result in data["zip_codes"]]

    # Write to CSV
    with open("ca_zip_codes.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["zip_code"])  # Write header
        for zip_code in sorted(set(ca_zip_codes)):  # Remove duplicates and sort
            writer.writerow([zip_code])

    print("Successfully wrote CA ZIP codes to ca_zip_codes.csv")

except requests.exceptions.RequestException as e:
    print(f"An error occurred during the API request: {e}")
except KeyError as e:
    print(f"An error occurred while parsing the JSON: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
