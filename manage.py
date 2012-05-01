#!/usr/bin/env python
# Copyright 2012 PAWS. All rights reserved.
# Date: 4/30/2012
# manager.py - Django manager file for the PAWS project.

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sdzoo.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
