# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["pling_publisher"]

package_data = {"": ["*"]}

install_requires = ["requests", "typer"]

entry_points = {"console_scripts": ["pling = pling_publisher.cli:app"]}

setup_kwargs = {
    "name": "pling-publisher",
    "version": "0.1.10",
    "description": "",
    "long_description": "# Pling Publisher\nTool to upload to [gnome-look.org](https://gnome-look.org), [store.kde.org](https://store.kde.org), [www.pling.com](https://https://www.pling.com/).\n\n![Build Status](https://github.com/dmzoneill/pling-publisher/actions/workflows/main.yml/badge.svg)\n\n\nYou can find this python module on [https://pypi.org/project/pling-publisher/](https://pypi.org/project/pling-publisher/)\n\n\n## Install\n```console\npip install pling-publisher\n```\n\n## How to use\n```console\npling build # build an archive from the current folder.\npling publish --username <USERNAME> --password <PASSWORD> --project-id <PROJECT_ID> --file <PATH>\npling --help # for help :)\n```\n\nYou can also provide your username, password and project_id via environment variables (PLING_USERNAME, PLING_PASSWORD, PLING_PROJECT_ID).\n\n\n## Support\nFeel free to submit a pull request\n",
    "author": "David O Neill",
    "author_email": "dmz.oneill@gmail.com",
    "maintainer": None,
    "maintainer_email": None,
    "url": "https://github.com/dmzoneill/pling-publisher",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.8,<4.0",
}


setup(**setup_kwargs)
