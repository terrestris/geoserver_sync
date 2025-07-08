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

import os
from util.http import get, get_rest, post_rest, put_rest
from typing import Optional
from model.models import Result, FailedObject

def sync(workspaces: str, source_url: str, source_auth: tuple, target_url: str, target_auth: tuple):
    """
    Fetch all styles (with and without workspace) from the source GeoServer and create them on the target GeoServer.
    """

    success_styles = []
    failed_styles = []

    # create styles without workspace
    styles_no_ws_results = sync_ws_styles(None, source_url, source_auth, target_url, target_auth)
    success_styles.extend(styles_no_ws_results.success_objects)
    failed_styles.extend(styles_no_ws_results.failed_objects)

    # create styles of each workspace
    for workspace in workspaces:
        styles_ws_results = sync_ws_styles(workspace, source_url, source_auth, target_url, target_auth)
        success_styles.extend(styles_ws_results.success_objects)
        failed_styles.extend(styles_ws_results.failed_objects)

    return Result(success_objects=success_styles, failed_objects=failed_styles)


def sync_ws_styles(workspace: Optional[str], source_url: str, source_auth: tuple, target_url: str, target_auth: tuple):
    success_styles = []
    failed_styles = []

    if workspace is None:
        workspace_prefix = ""
    else:
        workspace_prefix = "workspaces/" + workspace + "/"

    styles_rest_path = workspace_prefix + "styles"

    result = get_rest(styles_rest_path, source_url, source_auth)
    if not result:
        failed = FailedObject(name="None", reason="Failed to fetch styles from source")
        failed_styles.append(failed)
        return Result(success_objects=success_styles, failed_objects=failed_styles)

    styles_json = result.get("styles", {}) # type: ignore

    if not styles_json:
        # we do not append a failed object here, as it is not an error if there are no styles
        return Result(success_objects=success_styles, failed_objects=failed_styles)

    styles = styles_json.get("style", []) # type: ignore
    print(f"[*] Found {len(styles)} styles for workspace '{workspace}' on source")

    for style in styles:
        href = style["href"]
        name = style["name"]

        # skip default styles that always exist
        if workspace is None and name in ["point", "line", "polygon", "raster", "generic"]:
            print(f"[!] Skipping default style '{name}'")
            continue

        style_obj = get(href, source_auth)

        style_name = style_obj.get("style", {}).get("name") # type: ignore

        if workspace_prefix == "":
            fq_style_name = style_name
        else:
            fq_style_name = f"{workspace}:{style_name}"


        # we have 2 steps for styles
        # 1. create the style entry that references the SLD
        # 2. create the SLD itself
        post_result = post_rest(styles_rest_path, target_url, target_auth, style_obj) # type: ignore

        if post_result == True:
            print(f"[+] Created style entry for '{fq_style_name}' on target (1/2)")

            sld_url = os.path.splitext(href)[0] + ".sld"
            sld_response = get(sld_url, source_auth, False)

            if sld_response is None:
                err_msg_tpl = f"[!] Could not fetch SLD from '{sld_url}' from source (2/2)"
                failed_style = FailedObject(name=fq_style_name, reason=err_msg_tpl)
                failed_styles.append(failed_style)
                print(f"[!] {err_msg_tpl}")
                continue

            if sld_response.ok:
                headers = {"Content-Type": "application/vnd.ogc.sld+xml"}
                sld_put_path = styles_rest_path + "/" + style_name

                put_result = put_rest(sld_put_path, target_url, target_auth, sld_response.text, headers, False) # type: ignore

                if put_result == True:
                    print(f"[+] Created SLD for '{fq_style_name}' on target (2/2)")
                    success_styles.append(fq_style_name)
                else:
                    err_msg_tpl = f"[!] Could not create SLD for style '{fq_style_name}' on target (2/2)"
                    failed_style = FailedObject(name=fq_style_name, reason=err_msg_tpl)
                    failed_styles.append(failed_style)
                    print(f"[!] {err_msg_tpl}")
                    continue
            else:
                err_msg_tpl = f"[!] Could not fetch SLD for style '{fq_style_name}' from source (2/2)"
                failed_style = FailedObject(name=fq_style_name, reason=err_msg_tpl)
                failed_styles.append(failed_style)
                print(f"[!] {err_msg_tpl}")
                continue

        else:
            err_msg_tpl = f"Failed to create style '{fq_style_name}' on target: {post_result}"
            failed_style = FailedObject(name=fq_style_name, reason=err_msg_tpl)
            failed_styles.append(failed_style)
            print(f"[!] {err_msg_tpl}")
            continue

    return Result(success_objects=success_styles, failed_objects=failed_styles)
