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
from model.models import Result, FailedObject

def sync(workspaces: list[str], source_url: str, source_auth: tuple, target_url: str, target_auth: tuple):
    """
    Fetch all layers for a given workspace from the source GeoServer and create them on the target GeoServer.
    """

    success_layers = []
    failed_layers = []
    # created_layers = []

    for workspace in workspaces:

        for layer_type in ["featureTypes", "coverages", "wmsLayers", "wmtsLayers"]:
            rest_path = "workspaces/" + workspace + "/" + layer_type.lower()
            get_result = get_rest(rest_path, source_url, source_auth)

            if not get_result:
                failed = FailedObject(name="None", reason=f"Failed to fetch layer type '{layer_type}' from source")
                failed_layers.append(failed)
                continue

            layers_obj = get_result.get(layer_type, {}) # type: ignore
            if not layers_obj:
                # this is not an error as there might be no layers
                continue

            layers = layers_obj.get(layer_type[:-1], [])

            print(f"[*] Found {len(layers)} layers of type '{layer_type}' in workspace '{workspace}'")

            for layer in layers:
                href = layer["href"]

                layer_result = get(href, source_auth)

                if layer_result is None:
                    failed = FailedObject(name=layer.get("name", "Unknown"), reason=f"Failed to fetch layer details from '{href}'")
                    failed_layers.append(failed)
                    print(f"[!] {failed.reason}")
                    continue

                layer_obj = layer_result.get(layer_type[:-1], {}) # type: ignore
                if not layer_obj:
                    failed = FailedObject(name=layer.get("name", "Unknown"), reason=f"Layer object is empty for '{href}'")
                    failed_layers.append(failed)
                    print(f"[!] {failed.reason}")
                    continue

                layer_name = layer_obj.get("name")
                store = layer_obj.get("store", {})

                if not store:
                    err_msg_tpl = f"[!] Could not create layer '{workspace}:{layer_name}' - no store found in layer object."
                    failed = FailedObject(name=layer_name, reason=err_msg_tpl)
                    failed_layers.append(failed)
                    print(f"{err_msg_tpl}")
                    continue

                store_name_parts = store.get("name").split(":")

                # Determine the store name as we need it to create the layer on the target GeoServer
                if len(store_name_parts) == 2 and store_name_parts[0] == workspace:
                    store_name = store_name_parts[1]
                else:
                    err_msg_tpl = f"[!] Could not create layer '{workspace}:{layer_name}' - invalid store format. Expected 'workspace:store_name'."
                    failed = FailedObject(name=layer_name, reason=err_msg_tpl)
                    failed_layers.append(failed)
                    print(f"{err_msg_tpl}")
                    continue

                if layer_type == "featureTypes":
                    # for feature type sources it is important to be posted against the "/workspaces/.../datastores/.../..." endpoint
                    rest_path = "workspaces/" + workspace + "/datastores/" + store_name + "/" + layer_type.lower()

                post_result = post_rest(rest_path, target_url, target_auth, layer_result) # type: ignore

                if post_result == True:
                    print(f"[+] Created layer '{workspace}:{layer_name}' of type '{layer_type[:-1]}' on target")

                    # we need to update to set styling, timing or caching properties
                    update_result = update_layer(workspace, layer_name, source_url, source_auth, target_url, target_auth)

                    if update_result == True:
                        print(f"[+] Updated layer config for '{workspace}:{layer_name}' on target")
                        success_layers.append(workspace + ":" + layer_name)
                    else:
                        err_msg_tpl = f"[!] Failed to update layer '{workspace}:{layer_name}' on target"
                        failed = FailedObject(name=layer_name, reason=err_msg_tpl)
                        failed_layers.append(failed)
                        print(f"{err_msg_tpl}")
                else:
                    err_msg_tpl = f"[!] Could not create layer '{workspace}:{layer_name}' of type '{layer_type[:-1]}' on target: {post_result}"
                    failed = FailedObject(name=layer_name, reason=err_msg_tpl)
                    failed_layers.append(failed)
                    print(f"{err_msg_tpl}")

    return Result(success_objects=success_layers, failed_objects=failed_layers)


def update_layer(workspace: str, layer_name: str, source_url: str, source_auth: tuple, target_url: str, target_auth: tuple):
    rest_path = "workspaces/" + workspace + "/layers/" + layer_name
    layer_settings = get_rest(rest_path, source_url, source_auth)

    if not layer_settings:
        err_msg_tpl = f"[!] Could not fetch layer settings for '{workspace}:{layer_name}' from source"
        print(f"{err_msg_tpl}")
        return err_msg_tpl

    # We need to post the layer settings to the target GeoServer
    put_result = put_rest(rest_path, target_url, target_auth, layer_settings) # type: ignore

    return put_result
