#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2022-present Linaro Limited
#
# SPDX-License-Identifier: MIT


import logging
import os
import re
import sys
import requests
from pathlib import Path
from squad_client.core.api import SquadApi
from squad_client.core.models import Squad, Build, TestRun
from squad_client.shortcuts import download_tests as download
from squad_client.shortcuts import get_build
from squad_client.utils import getid, first

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

squad_host_url = "https://qa-reports.linaro.org/"
SquadApi.configure(cache=3600, url=os.getenv("SQUAD_HOST",squad_host_url))

def get_file(path):
    print(f"Getting file from {path}")
    if re.search(r'https?://', path):
        request = requests.get(path, allow_redirects=True)
        request.raise_for_status()
        filename = path.split('/')[-1]
        with open(filename, 'wb') as f:
            f.write(request.content)
        return filename
    elif os.path.exists(path):
        return path
    else:
        raise Exception(f"Path {path} not found")


def find_good_build(base_build, project, environment, build_name, suite_name):
    builds = project.builds(id__lt=base_build.id, ordering="-id", count=10).values()
    for build in builds:
        logger.debug(f"Trying to find good test in build \"{build.version}\"")
        for testrun in build.testruns(environment=environment.id, prefetch_metadata=True).values():
            logger.debug(f"  - Trying to find {build_name} in {testrun.job_url}")
            if build_name == testrun.metadata.build_name or \
            testrun.metadata.build_name in ['gcc-12-lkftconfig',
                                            'gcc-11-lkftconfig',
                                            'gcc-10-lkftconfig']:
                logger.debug(f"    - Yay, found it, now looking for a passing {suite_name}")
                #candidate_test = first(testrun.tests(metadata__suite=suite_name,
                #                                     result=True))
                candidate_test = first(testrun.tests(metadata__suite=suite_name,
                                                     completed=True))
                if candidate_test is None:
                    logger.debug(f"      - no test in here :(")
                    continue
                logger.debug("************** FOUND IT *************")
                print(testrun)
                return build,testrun
    return None, None


def get_single_run(group, project, build_version, device_name, build_name,
                   suite_name, test_name, debug):
    if debug:
        logger.setLevel(level=logging.DEBUG)

    base_group = Squad().group(group)
    if base_group is None:
        logger.error(f"Get group failed. Group not found: '{group}'.")
        return None, None

    base_project = base_group.project(project)
    if base_project is None:
        logger.error(f"Get project failed. project not found: '{project}'.")
        return None, None

    build = get_build(build_version, base_project)
    if build is None:
        logger.error(f"Get build failed. build not found: '{build}'.")
        return None, None

    logger.debug(f"group: {group}, project: {project}, build: {build}, device: {device_name}, build-name: {build_name}, suite: {suite_name}, test: {test_name})")
    environment = base_project.environment(device_name)

    good_build, testrun = find_good_build(build, base_project, environment, build_name, suite_name)
    print("====================================")
    print(f"build_name: {testrun.metadata.build_name}")
    logger.debug(f"Testrun id {testrun.id}")
    #download_url = testrun.metadata.download_url
    #if download_url is None:
    #    if testrun.metadata.config is None:
    #        print("There is no way to determine download_url")
    #        return None, None
    #    download_url = testrun.metadata.config.replace("config", "")

    build_cmdline = ""
    tuxrun = get_file(f"{testrun.job_url}/reproducer")
    for line in Path(tuxrun).read_text(encoding="utf-8").split("\n"):
        if 'tuxrun --runtime' in line:
            line = re.sub("--tests \S+ ", "", line)
            line = re.sub(f"{suite_name}=\S+", "--timeouts command=10", line)
            build_cmdline = os.path.join(build_cmdline + line.strip() + ' --save-outputs --log-file -"').strip()

    build_cmdline = build_cmdline.replace('-"', f'- -- \'cd /opt/ltp && ./runltp -s {test_name}\'')
    return build, build_cmdline
