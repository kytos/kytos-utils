"""Module to include all constants in kytos-utils."""
import os
from pathlib import Path

BASE_ENV = Path(os.environ.get('VIRTUAL_ENV', '/'))
