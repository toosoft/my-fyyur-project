import requests

# Replace with your actual API token and store hash
store_hash = 'kqw14s7hk2'
api_token = 'gdk5cbgxsevvah9669ib22s25x90dc0'

# Define the API endpoint
api_url = f'https://api.bigcommerce.com/stores/{store_hash}/v3/content/pages'

# Set up headers with the API token
headers = {
    'Content-Type': 'application/json',
    'X-Auth-Token': api_token,
}
print('yes')
# Make the GET request to retrieve the list of pages
response = requests.get(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    pages_data = response.json()

    # Loop through the pages to find the cart page
    for page in pages_data['data']:
        if page['name'] == 'Cart':  # Adjust the name as needed
            cart_page_id = page['id']
            print(f'Cart Page ID: {cart_page_id}')
else:
    print(f'Error: {response.status_code}')
