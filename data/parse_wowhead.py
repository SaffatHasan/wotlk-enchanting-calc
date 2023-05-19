import requests
import json
from bs4 import BeautifulSoup

# specify the URL of the website
url = "https://www.wowhead.com/wotlk/spells/professions/enchanting"

# send a GET request to the website
response = requests.get(url)

# create a Beautiful Soup object to parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# find the table with class "listmodeview-mode-default"
# table = soup.find('table', {'class': 'listmodeview-mode-default'})

# if table is None:
#     with open("logs.txt", 'w') as f:
#         f.write(str(soup))

# # find all rows with class "listview-row"
# rows = table.find_all('tr', {'class': 'listview-row'})

# Find the script tag containing the JSON data
scripts = soup.find_all("script")

# Find the script tag that has the listviewspells variable
script_tag = next(filter( lambda s: "listviewspells" in s.text, scripts ))


# Extract the JSON data from the script tag
json_text = script_tag.text.strip().split("listviewspells", 1)[1].split(" = ")[1].split(";", 1)[0]

# Parse the JSON data into a Python object
with open("logs.txt", 'w') as f:
    f.write(json_text)

json_data = json.loads(json_text)

# Print the extracted JSON data
print(json_data)
