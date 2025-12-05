#!/usr/bin/env python3
"""
Test file with only imports to verify import block extraction
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
import json
import yaml

from .local_module import local_function
from ..parent_module import ParentClass

try:
    import external_lib
except ImportError:
    pass

# Relative imports
from . import sibling_module
from .subpackage import specific_function

# Aliased imports
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# Star import (should be captured)
from math import *

# Conditional import
if sys.version_info >= (3, 8):
    import new_feature
