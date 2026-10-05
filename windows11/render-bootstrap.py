#!/usr/bin/env python3
"""Render private Windows proof bootstrap files; never prints credentials.

Install mode partitions/wipes disk 0. Clone mode only specialises a sealed root.
This is operator proof tooling, not the workspace API credential contract.
"""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import xml.etree.ElementTree as ET

NS = "urn:schemas-microsoft-com:unattend"
WCM = "http://schemas.microsoft.com/WMIConfig/2002/State"
ET.register_namespace("", NS)
ET.register_namespace("wcm", WCM)


def element(parent, tag, text=None, **attributes):
    child = ET.SubElement(parent, "{" + NS + "}" + tag, attributes)
    if text is not None:
        child.text = str(text)
    return child


def component(settings, name):
    return element(settings, "component", name=name, processorArchitecture="amd64",
                   publicKeyToken="31bf3856ad364e35", language="neutral", versionScope="nonSxS")


def answer_file(mode, hostname, username, password, image_name="Windows 11 Pro"):
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]{0,14}", hostname):
        raise ValueError("hostname must start with a letter and contain at most 15 letters/digits/hyphens")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,19}", username) or username.lower() in (
            "administrator", "guest", "defaultaccount", "wdagutilityaccount"):
        raise ValueError("choose a non-reserved local username (1–20 letters/digits/underscore/hyphen)")
    if mode not in ("install", "clone"):
        raise ValueError("mode must be install or clone")
    root = ET.Element("{" + NS + "}unattend")
    if mode == "install":
        settings = element(root, "settings", **{"pass": "windowsPE"})
        international = component(settings, "Microsoft-Windows-International-Core-WinPE")
        ui = element(international, "SetupUILanguage")
        element(ui, "UILanguage", "en-US")
        for key in ("InputLocale", "SystemLocale", "UILanguage", "UserLocale"):
            element(international, key, "en-US")
        setup = component(settings, "Microsoft-Windows-Setup")
        commands = element(setup, "RunSynchronous")
        command = element(commands, "RunSynchronousCommand", **{"{" + WCM + "}action": "add"})
        element(command, "Order", 1)
        element(command, "Path", r"cmd /c for %d in (C D E F G H I J K) do @if exist %d:\viostor\w11\amd64\viostor.inf (subst V: %d:\ & drvload %d:\viostor\w11\amd64\viostor.inf)")
        configuration = element(setup, "DiskConfiguration")
        disk = element(configuration, "Disk", **{"{" + WCM + "}action": "add"})
        element(disk, "DiskID", 0)
        element(disk, "WillWipeDisk", "true")
        partitions = element(disk, "CreatePartitions")
        for order, kind, size in ((1, "EFI", 260), (2, "MSR", 16), (3, "Primary", None)):
            partition = element(partitions, "CreatePartition", **{"{" + WCM + "}action": "add"})
            element(partition, "Order", order)
            element(partition, "Type", kind)
            element(partition, "Size" if size else "Extend", size if size else "true")
        modifications = element(disk, "ModifyPartitions")
        for order, number, fmt, label, letter in ((1, 1, "FAT32", "System", None),
                                                (2, 3, "NTFS", "Windows", "C")):
            partition = element(modifications, "ModifyPartition", **{"{" + WCM + "}action": "add"})
            for key, value in (("Order", order), ("PartitionID", number), ("Format", fmt), ("Label", label)):
                element(partition, key, value)
            if letter:
                element(partition, "Letter", letter)
        element(configuration, "WillShowUI", "OnError")
        image = element(element(setup, "ImageInstall"), "OSImage")
        metadata = element(element(image, "InstallFrom"), "MetaData", **{"{" + WCM + "}action": "add"})
        element(metadata, "Key", "/IMAGE/NAME")
        element(metadata, "Value", image_name)
        target = element(image, "InstallTo")
        element(target, "DiskID", 0)
        element(target, "PartitionID", 3)
        element(image, "WillShowUI", "OnError")
        user = element(setup, "UserData")
        element(user, "AcceptEula", "true")
        key = element(user, "ProductKey")
        element(key, "Key", "")
        element(key, "WillShowUI", "Never")
        # drvload only loads the installer kernel. Native offline servicing
        # must also inject the boot-critical driver into the installed root.
        # V: is an alias of the discovered driver ISO for this WinPE session.
        offline = element(root, "settings", **{"pass": "offlineServicing"})
        customisations = component(offline, "Microsoft-Windows-PnpCustomizationsNonWinPE")
        paths = element(customisations, "DriverPaths")
        for order, driver in enumerate(("viostor", "NetKVM", "vioserial", "Balloon"), start=1):
            path = element(paths, "PathAndCredentials", **{"{" + WCM + "}action": "add",
                           "{" + WCM + "}keyValue": str(order)})
            element(path, "Path", f"V:\\{driver}\\w11\\amd64")
    settings = element(root, "settings", **{"pass": "specialize"})
    shell = component(settings, "Microsoft-Windows-Shell-Setup")
    element(shell, "ComputerName", hostname)
    element(shell, "TimeZone", "UTC")
    if mode == "install":
        deployment = component(settings, "Microsoft-Windows-Deployment")
        commands = element(deployment, "RunSynchronous")
        command = element(commands, "RunSynchronousCommand", **{"{" + WCM + "}action": "add"})
        element(command, "Order", 1)
        # Deployment RunSynchronous Path is limited to 259 characters. Keep
        # script contents on Sysprep media rather than embedding a long command.
        element(command, "Path", r'cmd /v:on /c "for %d in (D E F G H I J K L M N O P Q R S T U V W Y Z) do @if exist %d:\configure.ps1 (powershell.exe -NoProfile -ExecutionPolicy Bypass -File %d:\configure.ps1 & exit /b !errorlevel!) & exit /b 1"')
    settings = element(root, "settings", **{"pass": "oobeSystem"})
    international = component(settings, "Microsoft-Windows-International-Core")
    for key in ("InputLocale", "SystemLocale", "UILanguage", "UserLocale"):
        element(international, key, "en-US")
    shell = component(settings, "Microsoft-Windows-Shell-Setup")
    oobe = element(shell, "OOBE")
    for key in ("HideEULAPage", "HideOnlineAccountScreens", "HideWirelessSetupInOOBE"):
        element(oobe, key, "true")
    element(oobe, "ProtectYourPC", 3)
    accounts = element(element(shell, "UserAccounts"), "LocalAccounts")
    account = element(accounts, "LocalAccount", **{"{" + WCM + "}action": "add"})
    for key, value in (("Name", username), ("DisplayName", "Workspace"), ("Group", "Administrators")):
        element(account, key, value)
    secret = element(account, "Password")
    element(secret, "Value", password)
    element(secret, "PlainText", "true")
    ET.indent(root)
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def write_private(path, value):
    # Never overwrite an existing bootstrap/credential generation accidentally.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as output:
        output.write(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("install", "clone"), required=True)
    parser.add_argument("--namespace", default="windows11-proof")
    parser.add_argument("--secret-name", required=True)
    parser.add_argument("--hostname", default=None)
    parser.add_argument("--username", default="workspace")
    parser.add_argument("--image-name", default="Windows 11 Pro")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    for value in (args.namespace, args.secret_name):
        if len(value) > 63 or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", value):
            parser.error("namespace and Secret name must be DNS labels")
    hostname = args.hostname or "KW-" + secrets.token_hex(6).upper()
    password = secrets.token_urlsafe(24) + "!9aA"
    xml = answer_file(args.mode, hostname, args.username, password, args.image_name)
    args.output_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
    secret = {"apiVersion": "v1", "kind": "Secret",
              "metadata": {"name": args.secret_name, "namespace": args.namespace},
              "type": "Opaque", "stringData": {"autounattend.xml": xml}}
    if args.mode == "install":
        secret["stringData"]["configure.ps1"] = Path(__file__).with_name("Configure-Guest.ps1").read_text()
    write_private(args.output_dir / "bootstrap-secret.json", json.dumps(secret, indent=2))
    write_private(args.output_dir / "credentials.json", json.dumps(
        {"username": args.username, "password": password, "hostname": hostname}, indent=2))
    print("Private bootstrap-secret.json and credentials.json created in", args.output_dir)


if __name__ == "__main__":
    main()
