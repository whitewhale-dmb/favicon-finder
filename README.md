# Favicon-finder.py
This script is designed to take a favicon URL, or page URL to retrieve favicons from, and then generate Shodan links to all hosts which have the same favicon, by using the favicon file hash. Can also retrieve results details through the API. This technique can be useful for finding exposed hosts behind Cloudflare and other reverse proxies, and is based on [Favicon Hashing and Hunting With Shodan](https://www.iblue.team/general-notes-1/favicon-hashing-and-hunting-with-shodan).

# Add API key
```
./favicon-finder.py -a <API_KEY>
``` 

# Search for hosts with any matching favicons from a page
```
./favicon-finder.py -u https://github.com
```

# Search for hosts matching a specific favicon
```
./favicon-finder.py -u https://github.com/favicon.ico
```
