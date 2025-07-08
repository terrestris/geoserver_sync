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

from sync.workspaces import sync as sync_workspaces
from sync.datastores import sync as sync_datastores
from sync.styles import sync as sync_styles
from sync.layers import sync as sync_layers
from sync.layergroups import sync as sync_layergroups
from util.config import get_config
from util.log import log_results

def main():

    # Load config
    config = get_config()

    # Config for source GeoServer
    source_url = config["source"]["url"]
    source_user = config["source"]["user"]
    source_password = config["source"]["password"]
    source_auth = (source_user, source_password)

    # Config for target GeoServer
    target_url = config["target"]["url"]
    target_user = config["target"]["user"]
    target_password = config["target"]["password"]
    target_auth = (target_user, target_password)

    # Check if all required config values are set
    if None in [source_url, source_user, source_password, target_url, target_user, target_password]:
        raise ValueError(
            "One or more required GeoServer config values are missing.")

    # start migration in a meaningful order
    print("[*] Starting synchronization process...")
    workspace_results = sync_workspaces(
        source_url, source_auth, target_url, target_auth)  # type: ignore
    created_workspaces = workspace_results.success_objects

    if not created_workspaces or len(created_workspaces) == 0:
        print("[!] No workspaces were created. Exiting synchronization process.")
        return

    store_results = sync_datastores(
        created_workspaces, source_url, source_auth, target_url, target_auth)  # type: ignore

    styles_results = sync_styles(
        created_workspaces, source_url, source_auth, target_url, target_auth)  # type: ignore

    layers_results = sync_layers(
        created_workspaces, source_url, source_auth, target_url, target_auth)  # type: ignore

    layergroups_results = sync_layergroups(
        created_workspaces, source_url, source_auth, target_url, target_auth)  # type: ignore

    log_results(workspace_results, store_results, styles_results,
                layers_results, layergroups_results)


if __name__ == "__main__":
    main()
