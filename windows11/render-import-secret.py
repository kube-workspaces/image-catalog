#!/usr/bin/env python3
"""Render CDI pod-import credentials from private inline Docker registry auth.

CDI 1.61 pod import reads accessKeyId/secretKey, not .dockerconfigjson.
Never prints credentials. Output must be a new file outside source control.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import re


def import_secret(config, host, namespace, name):
    for value in (namespace, name):
        if len(value) > 63 or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", value):
            raise ValueError("namespace and Secret name must be DNS labels")
    if not host or "/" in host or any(c.isspace() for c in host):
        raise ValueError("registry host must be hostname[:port], without scheme or path")
    auths = config.get("auths", {})
    credentials = auths.get(host) or auths.get("https://" + host) or auths.get("https://" + host + "/v1/")
    if not credentials or not credentials.get("auth"):
        raise ValueError("registry needs inline auth; use crane auth login in a private DOCKER_CONFIG")
    try:
        username, password = base64.b64decode(credentials["auth"], validate=True).decode().split(":", 1)
    except (ValueError, UnicodeError) as error:
        raise ValueError("invalid inline registry auth") from error
    if not username or not password:
        raise ValueError("registry username and password/token must be nonempty")
    return {"apiVersion": "v1", "kind": "Secret",
            "metadata": {"name": name, "namespace": namespace}, "type": "Opaque",
            "stringData": {"accessKeyId": username, "secretKey": password}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker-config", required=True, type=Path, help="private config.json with inline auth")
    parser.add_argument("--registry-host", required=True)
    parser.add_argument("--namespace", default="windows11-proof")
    parser.add_argument("--secret-name", default="registry-import")
    parser.add_argument("--output", required=True, type=Path, help="new private output file")
    args = parser.parse_args()
    try:
        secret = import_secret(json.loads(args.docker_config.read_text()), args.registry_host,
                               args.namespace, args.secret_name)
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as output:
            json.dump(secret, output, indent=2)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Import Secret generation failed: {error}\n")
    print("Private CDI import Secret created")


if __name__ == "__main__":
    main()
