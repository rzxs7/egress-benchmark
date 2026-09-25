from pathlib import Path

import pytest

from egress_bench.config import load_config


def test_rejects_target_not_allowlisted(tmp_path: Path):
    p = tmp_path / "config.yaml"
    p.write_text(
        """
target:
  url: https://example.com/
  allowed_hosts: [localhost]
benchmark: {}
cases:
  baseline:
    enabled: true
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not in target.allowed_hosts"):
        load_config(p)
