"""Defines the hook endpoints for the dbt templater plugin."""

from dbt_osmosis.dbt_templater.templater import DbtTemplater
from sqlfluff.core.plugin import hookimpl


@hookimpl
def get_templaters():
    """Get templaters."""
    return [DbtTemplater]
