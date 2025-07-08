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

from util.http import get, get_rest, post_rest
from model.models import Result, FailedObject

def sync(source_url: str, source_auth: tuple, target_url: str, target_auth: tuple):
    """
    Fetch all namespaces from the source GeoServer and create them on the target GeoServer.
    This will also create the corresponding workspaces if they do not exist.
    """
    result = get_rest("namespaces", source_url, source_auth)
    if not result:
        failed_ns = FailedObject(name="None", reason="Failed to fetch namespaces from source")
        return Result(success_objects=[], failed_objects=[failed_ns])

    namespaces = result.get("namespaces", {}).get("namespace", []) # type: ignore
    print(f"[*] Found {len(namespaces)} namespaces on source")

    success_workspaces = []
    failed_workspaces = []
    err_msg_tpl = "Failed to fetch namespace details from '{href}'"

    for ns in namespaces:
        href = ns["href"]

        namespace_obj = get(href, source_auth)

        if namespace_obj is None:
            failed_ns = FailedObject(name=ns.get("name", "Unknown"), reason=err_msg_tpl.format(href=href))
            failed_workspaces.append(failed_ns)
            print(f"[!] {err_msg_tpl.format(href=href)}")
            continue

        ws_name = namespace_obj.get("namespace", {}).get("prefix") # type: ignore

        post_result = post_rest("namespaces", target_url, target_auth, namespace_obj) # type: ignore

        if post_result == True:
            success_workspaces.append(ws_name)
            print(f"[+] Created namespace '{ws_name}' on target")

        else:
            err_msg_tpl = f"Failed to create namespace '{ws_name}' on target: {post_result}"
            failed_ns = FailedObject(name=ws_name, reason=err_msg_tpl)
            failed_workspaces.append(failed_ns)
            print(f"[!] {err_msg_tpl}")

    return Result(success_objects=success_workspaces, failed_objects=failed_workspaces)
