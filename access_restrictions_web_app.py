import adal
import requests
import collections
import json

download_url = 'https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20191111.json'
subscription_id = '<<your subscription>'
resource_group = '<your resource group>'
app_service = '<your web app>'

#using AAD for authentication
tenant = "<your tenant id>"
authority_url = 'https://login.microsoftonline.com/' + tenant
client_id = "<your app id>"
client_secret = "<your app key>"
resource = 'https://management.azure.com/'

# 1. Get bearer token
context = adal.AuthenticationContext(authority_url)
token = context.acquire_token_with_client_credentials(resource, client_id, client_secret)
app_url = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + resource_group + '/providers/Microsoft.Web/sites/' + app_service + '/config/web'
headers = {'Authorization': 'Bearer ' + token['accessToken'], 'Content-Type': 'application/json'}
params = {'api-version': '2018-02-01'}

# 2. get file with IP addresses and these to wep app using Azure REST API
print('Beginning file download with requests')
response = requests.get(download_url)
ipaddresses_westeurope = json.loads((response.content.decode('utf-8')))['values']
priority=100
for value in ipaddresses_westeurope:
    if value['name'] == "AzureCloud.westeurope":
        body = collections.OrderedDict()
        properties = collections.OrderedDict()
        ipSecurityRestrictions = []
        for ipaddress in value['properties']['addressPrefixes']:
            print(ipaddress)

            ipSecurityRestrictions.append({"ipAddress": str(ipaddress), "action": "Allow", "tag": "Default", "priority": priority, "name": "rule " + str(priority)})
            priority+= 1

        properties['ipSecurityRestrictions'] = ipSecurityRestrictions
        body['properties'] = properties
        print(json.dumps(body, indent=4))

        r = requests.put(app_url, data=json.dumps(body), headers=headers, params=params)
        print(r.content)
