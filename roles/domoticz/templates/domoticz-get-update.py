#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Patrik Nilsson
# All rights reserved.
#
# This derivative work is sublicensed under the following conditions.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import urllib.request
import shutil
import subprocess
import os
import sys

def _check_for_update(url):
    params = '?type=command&param=checkforupdate'
    req = urllib.request.urlopen(str(url+params))
    response = req.read()
    return json.loads(response.decode('utf-8'))

def _download_update(dl_url, files):
    # There is no URL for the checksum, supplied by domoticz
    checksum_url = dl_url.replace('type=release', 'type=checksum')
    # Not sure why, but the default user-agent of urllib is blocked
    header = {'User-Agent': 'curl/7.38.0'}

    # Loop over urls and files in parallel
    urls = list([dl_url, checksum_url])
    for url, file_name in zip(urls, files):
        req = urllib.request.Request(url, headers=header)
        with urllib.request.urlopen(req) as response, \
             open(file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

def _verify_checksums(files):
    cmd = ['sha256sum','--status', '-c']
    return subprocess.call(cmd + [files[1]])

def main(dl_dir):
    query_url = 'http://127.0.0.1:8080/json.htm'
    files = ['update.tgz','update.tgz.sha256sum']

    # Change working directory to download directory
    os.chdir(dl_dir)

    # Check for available updates, using domoticz api. The benefit of
    # this is it will respect release channel chosen in the web gui.
    query_response = _check_for_update(query_url)
    dl_url = query_response['DomoticzUpdateURL']

    if query_response['HaveUpdate']:
        print ('Update available! Downloading...')

        # If checksum verification fails, retry twice
        retry = 0
        while not retry > 2:
            _download_update(dl_url, files)
            if _verify_checksums(files) == 0:
                break
            print ('Checksum missmatch, retrying...')
            retry += 1

        # If all retry attempts fail, remove archives
        if retry > 2:
            print('Download failed, cleaning up...')
            for f in files:
                os.remove(f)
            # Return failure so managers can notify of failure
            exit(1)
        else:
            print('Download completed successfully!')

main(sys.argv[1])
