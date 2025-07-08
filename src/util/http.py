#  Copyright © 2025-present terrestris GmbH & Co. KG
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0.txt
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
import requests

def get(url: str, auth: tuple, return_json_result: bool = True):
    response = requests.get(url, auth=auth)
    if response.ok:
        if return_json_result:
            return response.json()
        return response
    else:
        print(f"[!] Error while fetching {url}")
        print(f"[!] HTTP Status {response.status_code}: {response.text}")
        return None


def get_rest(path: str, base_url: str, auth: tuple, format: str = "json"):
    url = f"{base_url}/rest/{path}.{format}"
    return get(url, auth)


def extract_rest_sub_path_from_href(href: str, source_url: str):
    if href is None or href == "":
        print("[!] No href provided to fetch the resource.")
        return None

    # we would extract a subpath like "namespaces/test" from a href
    # "http://localhost:8081/geoserver/rest/namespaces/test.json"
    match = re.search(re.escape(source_url) + r'/rest/([^?]+?)(?:\.\w+)?$', href)

    if match:
        sub_path = match.group(1)
        return sub_path
    else:
        print(f"[!] Could not extract subpath from href: {href}")
        return None


def get_rest_by_href(href: str, source_url: str, auth: tuple, format: str = "json"):

    sub_path = extract_rest_sub_path_from_href(href, source_url)

    if not sub_path:
        return None

    source_obj = get_rest(sub_path, source_url, auth, format)

    if not source_obj:
        return None

    return source_obj


def post_rest(path: str, base_url: str, auth: tuple, data: dict, headers: dict = {"Content-Type": "application/json"}, post_json: bool = True):
    url = f"{base_url}/rest/{path}"

    if post_json:
        response = requests.post(url, json=data, auth=auth, headers=headers)
    else:
        response = requests.post(url, data=data, auth=auth, headers=headers)

    msg = None

    if response.status_code == 201:
        return True
    elif response.status_code == 401:
        msg = f"[!] Unauthorized – check credentials for {base_url}."
    elif response.status_code == 409:
        msg = f"[!] Target resource in '{path}' already exists."
    else:
        msg = f"[!] Error while posting to '{url}' - HTTP Status Code {response.status_code}: {response.text}"

    return msg


def put_rest(path: str, base_url: str, auth: tuple, data: dict, headers: dict = {"Content-Type": "application/json"}, put_json: bool = True):
    url = f"{base_url}/rest/{path}"

    if put_json:
        response = requests.put(url, json=data, auth=auth, headers=headers)
    else:
        response = requests.put(url, data=data, auth=auth, headers=headers)

    msg = None

    if response.ok:
        return True
    elif response.status_code == 401:
        msg = f"[!] Unauthorized – check credentials for {base_url}."
        return msg
    elif response.status_code == 409:
        msg = f"[!] Target resource in '{path}' already exists."
    else:
        msg = f"[!] Error while putting to '{url}' - HTTP Status Code {response.status_code}: {response.text}"

    return msg
