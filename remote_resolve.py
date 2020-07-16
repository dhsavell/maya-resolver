#!mayapy

from __future__ import print_function

import argparse
import os
import urllib2
import sys

desc = """
Fetches the resources for a Maya file from a remote repository. This is helpful for getting only one file and its
dependencies from a large asset dumps.

Resources are saved to ./resources. Any existing files in that directory will blindly be reused. Absolute paths
are skipped because we can't resolve those (yet).
"""

parser = argparse.ArgumentParser(description=desc)
parser.add_argument("filename", help="Maya scene to resolve")
parser.add_argument("--output", "-o", type=str, required=False, help="Output file (.mb)")
parser.add_argument(
    "--source",
    "-s",
    type=str,
    required=True,
    help="Base resource url. If source is `https://example.com`, script will look for `path/to/resource.tga` at `https://example.com/path/to/resource.tga`",
)
parser.add_argument("--temp-dir", "-t", type=str, default="resources")
args = parser.parse_args(sys.argv[1:])

filename = args.filename
output = args.output or os.path.splitext(filename)[0] + "_LocalPaths.mb"
output_type = "mayaBinary"

if output.endswith("ma"):
    output_type = "mayaAscii"

import maya.standalone

maya.standalone.initialize()

import maya.cmds as cmds

cmds.file(filename, open=True)
workspace = cmds.workspace(q=True, rd=True)

downloaded = 0
failed = 0
reused = 0

for d in cmds.filePathEditor(query=True, listDirectories="", unresolved=True):
    files = cmds.filePathEditor(query=True, listFiles=d, unresolved=True, withAttribute=True)
    if not files:
        print("no missing files to resolve in", d)
        continue

    for (f, n) in zip(*[iter(files)] * 2):
        target_path = os.path.join(d, f)
        try:
            missing_file = os.path.relpath(target_path, start=workspace)
        except ValueError:
            print("can't resolve", target_path)
            failed += 1
            continue

        local_path = os.path.join(args.temp_dir, missing_file)
        local_dir = os.path.dirname(local_path)

        if not os.path.isfile(local_path):
            if not os.path.isdir(local_dir):
                os.makedirs(local_dir)
            remote_path = args.source + "/" + missing_file.replace("\\", "/")
            try:
                print("downloading", remote_path, "...", end=" ")
                with open(local_path, "wb") as fp:
                    fp.write(urllib2.urlopen(remote_path).read())
                print("done!")
                downloaded += 1
            except urllib2.HTTPError, e:
                print(e)
                failed += 1
        else:
            reused += 1

        cmds.filePathEditor(n, repath=local_dir)

print()
print("downloaded\t", downloaded)
print("reused\t\t", reused)
print("failed\t\t", failed)

print()
print("saving updated scene to", cmds.file(rename=os.path.abspath(output)))
cmds.file(force=True, save=True, type=output_type)
