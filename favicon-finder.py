#!/usr/bin/env python3

import mmh3
import requests
import codecs
import argparse
from urllib.parse import urlparse
from bs4 import BeautifulSoup

root = None

def retrieve_icon(url):
    response = requests.get(url)
    if response.status_code == 200:
        generate_link(response.content)
    else:
        print("[!] Unsuccessful response from the URL: {code}".format(code=response.status_code))

def generate_link(content):
    favicon = codecs.encode(content,"base64")
    hash = mmh3.hash(favicon)
    print("\033[32m[+] Shodan link: https://www.shodan.io/search?query=http.favicon.hash%3A{hash}\033[39m".format(hash=hash))

def find_icons(html):
    global root
    dom = BeautifulSoup(html, 'html.parser')
    links = dom.find_all('link', rel='icon')
    for link in links:
        linkText = link.get('href')
        if linkText.startswith("http") == False:
            linkText = "{scheme}://{netloc}{linkText}".format(scheme=root.scheme,netloc=root.netloc,linkText=linkText)
        print("[*] Found icon {}".format(linkText))
        retrieve_icon(linkText)

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(
                prog='favicon-finder',
                description='Takes a favicon URL and generates a search link for the icon''s hash on Shodan'
            )

    parser.add_argument('-u', '--url', help="The full URL of the favicon, including protocol", required=True)

    args = parser.parse_args()

    root = urlparse(args.url)

    if root.scheme.startswith("http") == False:
        print("[!] You must include the HTTP protocol in the URL")
        exit()    
    
    try:
        main_request = requests.get(args.url)
    except Exception as e:
        print("[!] Could not retrieve URL: {e}".format(e=str(e)))
        exit()

    if main_request.status_code != 200:
        print("[!] Unsuccessful response from the URL: {code}".format(code=main_request.status_code))
        exit()

    if main_request.headers['content-type'].startswith("text/html"):
        print("[*] Pulling icons from {}".format(args.url))
        find_icons(main_request.text)
        print('[*] Trying blind request to favicon.ico')
        blindUrl = "{scheme}://{netloc}/favicon.ico".format(scheme=root.scheme,netloc=root.netloc)
        retrieve_icon(blindUrl)
    else:
        print("[*] Interpretted direct link to icon file")
        generate_link(main_request.content)

