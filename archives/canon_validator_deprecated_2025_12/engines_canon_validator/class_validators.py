"""`class_validators` module is a backport module from V1."""

from venv.Lib.site-packages.pydantic._migration import getattr_migration

__getattr__ = getattr_migration(__name__)

