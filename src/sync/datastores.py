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

import getpass
from util.http import get, get_rest, post_rest
from model.models import Result, FailedObject

def sync(workspaces: list[str], source_url: str, source_auth: tuple, target_url: str, target_auth: tuple):
    """
    Fetch all datastores for a given workspace from the source GeoServer and create them on the target GeoServer.
    """

    success_stores = []
    failed_stores = []

    for workspace in workspaces:

        for store_type in ["dataStores", "coverageStores", "wmsStores", "wmtsStores"]:
            rest_path = "workspaces/" + workspace + "/" + store_type.lower()
            store_results = get_rest(rest_path, source_url, source_auth)

            if not store_results:
                msg = f"Failed to fetch stores of type '{store_type}' for workspace '{workspace}'"
                failed_stores.append(FailedObject(name=workspace, reason=msg))
                continue

            stores_obj = store_results.get(store_type, {}) # type: ignore
            if not stores_obj:
                continue

            stores = stores_obj.get(store_type[:-1], [])

            print(f"[*] Found {len(stores)} stores of type '{store_type}' in workspace '{workspace}'")

            err_msg_tpl = "Failed to fetch store details from '{href}'"

            for store in stores:
                href = store["href"]

                store_result = get(href, source_auth)

                if store_result is None:
                    failed_store = FailedObject(name=store.get("name", "Unknown"), reason=err_msg_tpl.format(href=href))
                    failed_stores.append(failed_store)
                    print(f"[!] {err_msg_tpl.format(href=href)}")
                    continue

                store_obj = store_result.get(store_type[:-1], {}) # type: ignore
                if not store_obj:
                    # we do not append a failed object here, as it is not an error if there are no stores
                    continue

                store_name = store_obj.get("name")
                store_obj_type = store_obj.get("type")

                # check if there is an entry named 'passwd'
                # to prompt the user for a password
                # this is necessary as GeoServer does not accept encrypted passwords here
                connection_params = store_obj.get("connectionParameters", {})
                if connection_params and "entry" in connection_params:
                    entries = connection_params["entry"]
                    for entry in entries:
                        if entry.get("@key") == "passwd":
                            passwd = getpass.getpass(f"[?] Please enter the password for datastore '{workspace}:{store_name}': ")
                            entry["$"] = passwd

                # same for the 'password' field in WMS datastores
                if store_obj_type == "WMS" and "password" in store_obj:
                    passwd = getpass.getpass(f"[?] Please enter the password for (cascaded) WMS datastore '{workspace}:{store_name}': ")
                    store_obj["password"] = passwd

                post_result = post_rest(rest_path, target_url, target_auth, store_result) # type: ignore

                if post_result == True:
                    success_stores.append(workspace + ":" + store_name)
                    print(f"[+] Created store '{store_name}' of type '{store_type[:-1]}' on target")
                else:
                    err_msg_tpl = f"Failed to create store '{store_name}' of type '{store_type[:-1]}' on target: {post_result}"
                    failed_store = FailedObject(name=store_name, reason=err_msg_tpl)
                    failed_stores.append(failed_store)
                    print(f"[!] {err_msg_tpl}")

    return Result(success_objects=success_stores, failed_objects=failed_stores)
