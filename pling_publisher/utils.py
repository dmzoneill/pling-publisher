"""Helpers for packaging a project and publishing it to pling.com."""

import base64
import os
import re
import sys
from urllib import parse
from zipfile import ZIP_DEFLATED, ZipFile

import requests
import typer

AUTHORITY = "www.pling.com"
BASE_URL = "https://" + AUTHORITY + "/"

BROWSER_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
    "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
)
UA_PLATFORM = "Mozilla/5.0 (X11; Linux x86_64)"
UA_ENGINE = "AppleWebKit/537.36 (KHTML, like Gecko)"
UA_BROWSER = "Chrome/109.0.0.0 Safari/537.36"
BROWSER_USER_AGENT = f"{UA_PLATFORM} {UA_ENGINE} {UA_BROWSER}"


def create_zip_file(file_path, target_dir):
    """Zip target_dir into file_path, skipping VCS and build artefacts."""
    directories_to_ignore = [
        ".git",
        ".github",
        "dist",
        ".gitignore",
        "Makefile",
        "setup.py",
    ]
    rootlen = len(target_dir) + 1

    with ZipFile(file_path, "w", ZIP_DEFLATED) as zipobj:
        for base, _dirs, files in os.walk(target_dir):
            if any(ignored in base for ignored in directories_to_ignore):
                continue

            for file in files:
                fn = os.path.join(base, file)
                zipobj.write(fn, fn[rootlen:])


def _browser_headers() -> dict:
    return {
        "authority": AUTHORITY,
        "accept": BROWSER_ACCEPT,
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "dnt": "1",
        "pragma": "no-cache",
        "referer": BASE_URL,
        "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": BROWSER_USER_AGENT,
    }


def _extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    if match is None:
        raise AttributeError(f"Pattern not found in page: {pattern}")
    return match.group(1)


def _login(
    client: requests.Session,
    headers: dict,
    username: str | None,
    password: str | None,
) -> None:
    login_data = {
        "csrf": "",
        "email": username,
        "password": password,
        "next": "/",
        "remember_me": "1",
    }

    client.get(BASE_URL, headers=headers)
    login_page = client.get(BASE_URL + "login/", headers=headers)
    login_data["csrf"] = _extract(
        r"name=\"csrf\" value=\"(.*?)\"",
        login_page.content.decode("UTF-8"),
    )

    headers["referer"] = BASE_URL + "login/"
    login_response = client.post(BASE_URL + "login/", login_data, headers=headers)

    if b"Incorrect login and/or password" in login_response.content:
        typer.echo("failed login")
        sys.exit(1)


def upload(
    username: str | None,
    password: str | None,
    project_id: str,
    zipfile: str,
):
    """Log in to pling.com and upload zipfile to project_id."""
    with open(zipfile, "rb") as handle:
        the_file = base64.b64encode(handle.read())

    headers = _browser_headers()
    client = requests.Session()
    _login(client, headers, username, password)

    edit_page = client.get(BASE_URL + "p/" + project_id + "/edit", headers=headers)
    page = edit_page.content.decode("UTF-8")
    upload_url = _extract(r"var fileUri = '(.*?)'", page)
    post_data = {
        "collection_id": _extract(r"data-ppload-collection-id=\"(.*?)\"", page),
        "id": "1676575635",
        "owner_id": _extract(r"\"owner_id\", '(.*?)'", page),
        "format": "json",
        "client_id": _extract(r"client_id = '(.*?)'", page),
        "name": "file",
        "filename": "archive.tgz",
    }

    headers["accept"] = "application/json, text/javascript, */*; q=0.01"
    headers["origin"] = BASE_URL
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-site"
    del headers["sec-fetch-user"]
    del headers["upgrade-insecure-requests"]

    params = dict(parse.parse_qsl(parse.urlsplit(upload_url).query))
    files = {"file": (zipfile, the_file, "application/zip")}
    response = client.post(
        upload_url,
        params=params,
        headers=headers,
        data=post_data,
        files=files,
    )

    if '"status":"success"' in response.content.decode("UTF-8"):
        return True
    typer.echo("Failed publishing: " + zipfile)
    typer.echo("\n")
    typer.echo(response.content.decode("UTF-8"))
    return False
