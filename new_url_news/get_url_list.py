#!/usr/bin/env python3

import os
import subprocess
import sys
import urllib.request
from typing import Iterable, List, Tuple


def getURL(page):
    """

    :param page: html of web page (here: Python home page)
    :return: urls in that page
    """
    start_link = page.find("a href")
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url, end_quote


def getURLs(page):
    urls = []
    while True:
        url, n = getURL(page)
        page = page[n:]
        if url:
            urls.append(url)
        else:
            break
    return urls


def get_content(url: str):
    request = urllib.request.Request(
        url=url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'
        }
    )

    with urllib.request.urlopen(request) as response:
        return response.read().decode()


def get_unique_urls(page_url, old_urls: Iterable) -> Tuple[List[str], List[str]]:
    content = get_content(page_url)
    # matches = re.findall("", content)
    matches = getURLs(content)

    urls_keep = []
    url: str
    for url in matches:
        if url.startswith("/"):
            urls_keep.append(f"{page_url}{url}")
        elif url.startswith("http"):
            urls_keep.append(f"{url}")
        else:
            pass

    urls_set = set(urls_keep)
    urls_old_set = set(old_urls)
    urls_unique = []
    urls_new = []
    for url in urls_keep:
        if url in urls_set:
            if url not in urls_old_set:
                urls_new.append(url)
            urls_unique.append(url)
            urls_set.remove(url)
    return urls_unique, urls_new


def save_urls_file(urls: Iterable, filename: str):
    with open(filename, "w") as new_urls_file:
        for url in urls:
            new_urls_file.write(url + "\n")


def main():
    page_url = sys.argv[1]

    with open(page_url.replace("/", "-") + ".txt", "r") as file:
        old_urls = [line.rstrip() for line in file]

    urls_unique, urls_new = get_unique_urls(page_url, old_urls)

    save_urls_file(urls_unique, page_url.replace("/", "-") + ".txt")
    # save_urls_file(urls_new, page_url.replace("/", "-") + "_new.txt")

    for url in urls_new:
        # print(url)
        subprocess.call([os.path.expanduser("~/Documents/erinner_bot/t_msg"), url, "news.id"])
        # print(rc)


if __name__ == "__main__":
    main()
