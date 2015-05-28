#!/usr/bin/env python2

# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2014-2015 University of Nebraska at Omaha (UNO) and other
# contributors.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Usage: DoSPDX.py [--help] [options] (FILE | -i DOCID)

Options:
  -i, --doc-id=DOCID          Generate SPDX document from database
                                (required if FILE argument not specified)
  -n, --no-scan               Don't scan the package if SPDX data has not
                                already been generated
  -p, --print=FORMAT          Print SPDX document in specified format
                                (`tag' or `rdf')
  --comment=TEXT              Specify SPDX document comment section
  --creator=TEXT              Specify SPDX creator field
  --creator-comment=TEXT      Specify SPDX creator comment field
  --supplier=TEXT             Specify package supplier field
  --package-version=TEXT      Specify package version field
  --download-location=TEXT    Specify package download location field
  --originator=TEXT           Specify package originator field
  --home-page=TEXT            Specify package home page field
  --source-info=TEXT          Specify package source information field
  --license-comments=TEXT     Specify license comments field
  --description=TEXT          Specify package description field

Options taking a TEXT argument require double quotes around the argument.\
'''


import docopt
import os
import settings
import sys

format_map = {
    'tag': 'templates/2.0.tag',
    'rdf': 'templates/2.0.rdf',
}

def extract_fields(argv):
    fields = {
        'document_comment': argv['--comment'],
        'creator': argv['--creator'],
        'creator_comment': argv['--creator-comment'],
        'package_version': argv['--package-version'],
        'package_supplier': argv['--supplier'],
        'package_originator': argv['--originator'],
        'package_download_location': argv['--download-location'],
        'package_home_page': argv['--home-page'],
        'package_source_info': argv['--source-info'],
        'package_license_comments': argv['--license-comments'],
        'package_description': argv['--description']
    }
    for key in fields:
        fields[key] = fields[key] or ''
    return fields


def main():
    progname = os.path.basename(sys.argv[0])
    argv = docopt.docopt(doc=__doc__, version='0.0.1-dev')

    if argv['--doc-id'] is None and argv['FILE'] is None:
        print(progname + ": You must specify a file or document ID")
        print(progname + ": Try `" + progname + " --help' for more information.")
        sys.exit(1)

    fields = extract_fields(argv)
    package_path = argv['FILE']
    docid = argv['--doc-id']
    scan = not argv['--no-scan']
    output_format = argv['--print']

    if output_format not in ('tag', 'rdf', None):
        print(progname + ": Unknown output format '" + output_format + "'")
        print(progname + ": Try `" + progname + " --help' for more information.")
        sys.exit(1)

    # import not at top of file for performance reasons
    from spdx import SPDXDB

    with SPDXDB() as spdx:
        if docid is not None:
            document = spdx.fetch_doc(docid)
            if document is None:
                print('Document id {} not found in the database.'.format(docid))
                sys.exit(1)
        elif scan:
            docid = spdx.scan_package_create_doc(package_path)
            document = spdx.fetch_doc(docid)

    with SPDXDB() as spdx:
        if document is not None and output_format is not None:
            print(spdx.render_doc(document, format_map[output_format]))


if __name__ == "__main__":
    main()
