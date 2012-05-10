# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# Main Utility Enrichment importer
# This is utility script used to import species and enrichments into the
# database.

import fileinput

for line in fileinput.input():
  print line