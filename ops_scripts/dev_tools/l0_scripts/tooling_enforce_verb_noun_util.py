from __future__ import annotations

import logging
import re

'Brief description of functionality and purpose.'
'Brief description of functionality and purpose.'
_logger = logging.getLogger(__name__)
import shutil
import sys
from pathlib import Path
from typing import Any

for f in sys.argv[1:]:
    p: Any = Path(f)
    if re.match('^[a-z]+_[a-z_]+\\.py$', p.name):
        continue
    if p.parent.name.startswith('L2_'):
        NEW: Any = p.parent / f'invoke_{p.stem}.py'
    else:
        NEW: Any = p.parent / f'retrieve_{p.stem}.py'
    shutil.move(p, new)
