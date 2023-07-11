# Favicon-finder.py
This script is designed to take a favicon URL, or page URL to retrieve favicons from, and then generate Shodan links to all hosts which have the same favicon, by using the favicon file hash. This can be useful for finding exposed hosts behind Cloudflare and other reverse proxies.

Based on [Favicon Hashing and Hunting With Shodan](https://www.iblue.team/general-notes-1/favicon-hashing-and-hunting-with-shodan).

# Use
```
./favicon-finder.py -u https://github.com
```
