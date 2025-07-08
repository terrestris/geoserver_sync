# GeoServer Catalog Sync Tool

A python tool to migrate catalog info between two GeoServers via REST.
This can be used to migrate from a XML/file based catalog to a database based catalog (like in GS Cloud).
But in general you can use it between two GeoServer endpoints (whether GS cloud or not).

Currently the following data can be migrated:

- workspaces
- stores
- styles
- layers
- layer groups

Migration of settings (global, WMS, WFS, ...) is not yet implemented, but could be done easily in future.

## Adjust config

Adjust the `config.toml` to your environment or needs.

If you want to use a GeoServer available on your host, the internal docker IP `172.17.0.1` (or whatever it is in your case) can be used to access it from the sync container.


## Build & Run

You can run the python tool locally or in a docker container.

### Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Docker container

The local `config.toml` will be mounted to the container (to avoid building images that include passwords).

```bash
docker compose run --build --rm geoserver-sync
```

# Important Notes

## Passwords for Datastores

GeoServer does not accept encrypted (`crypt2:...`) password values via REST POSTs (as we GET them on the source side), but instead expects the raw password in the payload, which will then be stored encrypted by GeoServer.

So whenever the sync tool finds a password field/key in datastores, it will prompt the user for the raw password to be able to POST it.

Therefore you should also make sure to always use HTTPS secured GeoServers on target side!

There might be scenarios (for certain extensions?) that are not yet supported.


## Existing data

Some layer types require that the underlying data source (a shapefile, geopackage, geotiff) exists and is accessible at the time of creation/sync.
This means the target environment must be prepared regarding correctly mounted geodata (to match the structure of the source environment).


## Known issues

* SQL view based layer, see https://github.com/geoserver/geoserver-cloud/pull/679
* There might be uncovered scenarios for extensions: https://docs.geoserver.org/main/en/user/rest/api/datastores.html#extension
* GeoServer Cloud currently (06/2025) has a potential ImageMosaic bug: https://github.com/geoserver/geoserver-cloud/issues/630#issuecomment-2984082240
