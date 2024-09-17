import pandas as pd
import requests
from bs4 import BeautifulSoup

### Variables ###
# Strict mode forces all results to be either Yes/1 or No/0
# Anything else is converted
strict_mode = True
strict_replacement = 'Review'

# Numeric mode returns 1 and 0 instead of Yes and No, compatible with tfitzmac's 'resource capabilities' outputs.
numeric_mode = True

# If you want to include regions as well as resource groups and subscriptions, set this to True
# Strictly you might also want to set strict_replacement to '0' as a worst-case scenario, up to you
include_region_move = False

# URL of the web page
url = 'https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/move-support-resources'

### Let's get started! ###

# Write the header
file_name = 'azure_resource_migration_list.csv'
csv_file = open(file_name, 'w')
if (include_region_move == True):
    csv_file.writelines("Resource,Move Resource Group,Move Subscription,Move Region\n")
else:
    csv_file.writelines("Resource,Move Resource Group,Move Subscription\n")
csv_file.close()

# Send a GET request to the web page
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the anchor headers
ah = soup.find_all(lambda tag: tag.name == "h2")

for i, header in enumerate(ah):
    # We only want the sections that begin with 'Microsoft.'
    if "Microsoft." in header.get_text():
        resource_class = header.get_text() + "/"

        # Find the next table
        table = header.find_next("table")

        # Read the HTML table into a DataFrame
        df = pd.read_html(str(table))[0]
        df['Resource type'] = df['Resource type'].apply(lambda x: "{}{}".format(resource_class, x))

        if (strict_mode == True):
            #Force either Yes or No, otherwise replace with the strict replacement
            df.loc[~df["Resource group"].isin(["Yes","No"]), "Resource group"] = strict_replacement
            df.loc[~df["Subscription"].isin(["Yes","No"]), "Subscription"] = strict_replacement
            df.loc[~df["Region move"].isin(["Yes","No"]), "Region move"] = strict_replacement

        if (numeric_mode == True):
            #Convert Yes and No to 1 and 0
            df[df.isin(["Yes"])] = "1"
            df[df.isin(["No"])] = "0"

        if (include_region_move == False):
            df.drop('Region move', axis=1, inplace = True)

        # apply regular expression to remove white space from all strings in DataFrame
        df['Resource type'] = df['Resource type'].replace(r'\s+', '', regex=True)

        # Save the DataFrame to a CSV file
        df.to_csv(file_name, index=False, header=False, mode='a')

print("Tables have been saved to " + file_name)
