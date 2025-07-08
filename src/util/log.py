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

from model.models import Result

def log_results(workspaces_results: Result, store_results: Result, styles_results: Result, layers_results: Result, layergroups_results: Result):
    print("[*] Synchronization completed - Summary of successes:")

    created_workspaces = workspaces_results.success_objects
    created_stores = store_results.success_objects
    created_styles = styles_results.success_objects
    created_layers = layers_results.success_objects
    created_layergroups = layergroups_results.success_objects

    failed_workspaces = workspaces_results.failed_objects
    failed_stores = store_results.failed_objects
    failed_styles = styles_results.failed_objects
    failed_layers = layers_results.failed_objects
    failed_layergroups = layergroups_results.failed_objects

    if created_workspaces:
        print(
            f"[*] Created {len(created_workspaces)} workspaces on target GeoServer:")
        for ws in created_workspaces:
            print(f" - {ws}")
    else:
        print("[*] No new workspaces were created on the target GeoServer.")

    if created_stores:
        print(
            f"[*] Created {len(created_stores)} datastores on target GeoServer:")
        for store in created_stores:
            print(f" - {store}")
    else:
        print("[*] No new datastores were created on the target GeoServer.")

    if created_styles:
        print(f"[*] Created {len(created_styles)} styles on target GeoServer:")
        for style in created_styles:
            print(f" - {style}")
    else:
        print("[*] No new styles were created on the target GeoServer.")

    if created_layers:
        print(f"[*] Created {len(created_layers)} layers on target GeoServer:")
        for layer in created_layers:
            print(f" - {layer}")
    else:
        print("[*] No new layers were created on the target GeoServer.")

    if layergroups_results:
        print(
            f"[*] Created {len(created_layergroups)} layergroups on target GeoServer:")
        for layergroup in created_layergroups:
            print(f" - {layergroup}")
    else:
        print("[*] No new layergroups were created on the target GeoServer.")

    print("[*] Summary of fails and objects that could NOT be created:")

    if failed_workspaces:
        print(f"[*] Failed to create {len(failed_workspaces)} workspaces:")
        for failed in failed_workspaces:
            print(f" - {failed.name}: {failed.reason}")
    else:
        print("[*] No workspaces failed to be created on the target GeoServer.")

    if failed_stores:
        print(f"[*] Failed to create {len(failed_stores)} datastores:")
        for failed in failed_stores:
            print(f" - {failed.name}: {failed.reason}")
    else:
        print("[*] No datastores failed to be created on the target GeoServer.")

    if failed_styles:
        print(f"[*] Failed to create {len(failed_styles)} styles:")
        for failed in failed_styles:
            print(f" - {failed.name}: {failed.reason}")
    else:
        print("[*] No styles failed to be created on the target GeoServer.")

    if failed_layers:
        print(f"[*] Failed to create {len(failed_layers)} layers:")
        for failed in failed_layers:
            print(f" - {failed.name}: {failed.reason}")
    else:
        print("[*] No layers failed to be created on the target GeoServer.")

    if failed_layergroups:
        print(f"[*] Failed to create {len(failed_layergroups)} layergroups:")
        for failed in failed_layergroups:
            print(f" - {failed.name}: {failed.reason}")
    else:
        print("[*] No layergroups failed to be created on the target GeoServer.")
