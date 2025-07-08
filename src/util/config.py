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

import tomllib

config = None

def get_config(force: bool = False) -> dict:
    """
    Reads the configuration from the config.toml file.
    Returns a dictionary with the configuration.
    """
    global config
    try:
        if force or config is None:
            with open("config.toml", "rb") as f:
                config = tomllib.load(f)
        return config
    except FileNotFoundError:
        print("Configuration file 'config.toml' not found.")
        return {}
    except tomllib.TOMLDecodeError as e:
        print(f"Error decoding TOML file: {e}")
        return {}

