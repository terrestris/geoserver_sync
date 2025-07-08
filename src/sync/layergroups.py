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

from util.http import get, get_rest, post_rest, put_rest
from typing import Optional
from model.models import Result, FailedObject

def sync(workspaces: str, source_url: str, source_auth: tuple, target_url: str, target_auth: tuple):
    """
    Fetch all layergroups (with and without workspace) from the source GeoServer and create them on the target GeoServer.
    """

    success_layergroups = []
    failed_layergroups = []

    # create layergroups without workspace
    layergroups_no_ws_results = sync_ws_layergroups(None, source_url, source_auth, target_url, target_auth)
    success_layergroups.extend(layergroups_no_ws_results.success_objects)
    failed_layergroups.extend(layergroups_no_ws_results.failed_objects)

    # create layergroups for each workspace
    for workspace in workspaces:
        layergroups_ws_results = sync_ws_layergroups(workspace, source_url, source_auth, target_url, target_auth)
        success_layergroups.extend(layergroups_ws_results.success_objects)
        failed_layergroups.extend(layergroups_ws_results.failed_objects)

    return Result(success_objects=success_layergroups, failed_objects=failed_layergroups)


def sync_ws_layergroups(workspace: Optional[str], source_url: str, source_auth: tuple, target_url: str, target_auth: tuple):
    success_layergroups = []
    failed_layergroups = []

    if workspace is None:
        workspace_prefix = ""
    else:
        workspace_prefix = "workspaces/" + workspace + "/"

    layergroups_rest_path = workspace_prefix + "layergroups"

    result = get_rest(layergroups_rest_path, source_url, source_auth)
    if not result:
        failed = FailedObject(name="None", reason="Failed to fetch layergroups from source")
        failed_layergroups.append(failed)
        return Result(success_objects=success_layergroups, failed_objects=failed_layergroups)

    layergroups_json = result.get("layerGroups", {}) # type: ignore

    if not layergroups_json:
        # we do not append a failed object here, as it is not an error if there are no layergroups
        return Result(success_objects=success_layergroups, failed_objects=failed_layergroups)

    layergroups = layergroups_json.get("layerGroup", []) # type: ignore
    print(f"[*] Found {len(layergroups)} layergroups for workspace '{workspace}' on source")

    for layergroup in layergroups:
        href = layergroup["href"]

        layergroup_obj = get(href, source_auth)

        layergroup_name = layergroup_obj.get("layerGroup", {}).get("name") # type: ignore

        if workspace_prefix == "":
            fq_layergroup_name = layergroup_name
        else:
            fq_layergroup_name = f"{workspace}:{layergroup_name}"

        post_result = post_rest(layergroups_rest_path, target_url, target_auth, layergroup_obj) # type: ignore

        if post_result == True:
            print(f"[+] Created layergroup '{fq_layergroup_name}' on target")
            success_layergroups.append(fq_layergroup_name)

        else:
            err_msg_tpl = f"Failed to create layergroup '{fq_layergroup_name}' on target: {post_result}"
            failed_layergroup = FailedObject(name=fq_layergroup_name, reason=err_msg_tpl)
            failed_layergroups.append(failed_layergroup)
            print(f"[!] {err_msg_tpl}")
            continue

    return Result(success_objects=success_layergroups, failed_objects=failed_layergroups)
