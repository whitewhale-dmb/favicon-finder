#!/usr/bin/env python3

import shodan
import mmh3
import requests
import urllib.parse
import codecs
import argparse
import os
from dotenv import load_dotenv, find_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup

env_path = os.path.join(os.path.dirname(__file__), '.env')
env = load_dotenv(env_path)
root = None
api_key = os.getenv('shodanAPI')
hashes = []

def retrieve_icon(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("[+] Found default favicon.ico")
        generate_link(response.content)
    else:
        print("[!] Unsuccessful response from the URL: {code}".format(code=response.status_code))

def generate_link(content):
    global hashes
    favicon = codecs.encode(content,"base64")
    hash = str(mmh3.hash(favicon))
    hashes.append("http.favicon.hash:{}".format(hash))

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

def setup_api():
    global env_path
    apiKey = args.api.strip()
    f = open(env_path, "w")
    f.write("shodanAPI={}".format(apiKey))
    f.close()

def output_results():
    global hashes, api_key

    if hashes == []:
        exit("[!] No results found")
    
    query = " OR ".join(hashes)
    if api_key is not None:
        api = shodan.Shodan(api_key)
        try:
            results = api.search(query)
            print("[*] {} hosts found:".format(results['total']))
            print('')
            for result in results['matches']:
                print('\033[32m[+]\033[39m IP: {}'.format(result['ip_str']))
                print('    Hostname(s): {}'.format(", ".join(result['hostnames'])))
                print('    Port: {}'.format(result['port']))
                print('    OS: {}'.format(result['os']))
                print('    Organisation: {}'.format(result['org']))
                print('    Link: https://www.shodan.io/host/{}'.format(result['ip_str']))
                print('')
        except shodan.APIError as e:
            print('Shodan API Error: {}'.format(e))
    print("\033[32m[+] Complete Shodan search: https://www.shodan.io/search?query={query}\033[39m".format(query=urllib.parse.quote(query)))

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(
                prog='favicon-finder',
                description='Takes a favicon URL and generates a search link for the icon''s hash on Shodan'
            )

    parser.add_argument('-u', '--url', help="The full URL of the favicon, including protocol")
    parser.add_argument('-a', '--api', help="Optionally - Saves your Shodan API key to pull details into here")

    args = parser.parse_args()
    
    if args.api is not None:
        setup_api()
        exit("[*] API key saved. You can now run this without the --api parameter")
    else:
        if args.url is None:
            print("usage: favicon-finder [-h] [-u URL]/[-a API_KEY]")
            exit("favicon-finder: error: the following arguments are required: -u/--url")
        if env == False:
            print("Note: Your API key has not been set. Use --api <key> to set up API integration")


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
    
    output_results()
