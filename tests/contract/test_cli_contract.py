import os
"""CLI contract tests — CT-001 through CT-011 (IR-001, IR-002)."""
import subprocess
import sys
import tempfile
import struct
import zlib
from pathlib import Path
import pytest

PYTHON = sys.executable
ENV_PATH = "src"


def cli(*args, input_data=None, cwd=None):
    env = {"PYTHONPATH": ENV_PATH}
    full_env = {**os.environ, **env}
    return subprocess.run(
        [PYTHON, "-m", "qr_transfer.cli", *args],
        capture_output=True, cwd=cwd or ".", env=full_env
    )


# CT-006: --help
def test_help_exit_0():
    r = cli("--help")
    assert r.returncode == 0
    assert b"encode" in r.stdout
    assert b"decode" in r.stdout
    assert b"verify" in r.stdout
    assert b"info" in r.stdout


def test_encode_help():
    r = cli("encode", "--help")
    assert r.returncode == 0
    assert b"grid" in r.stdout.lower() or b"grid-size" in r.stdout.lower()


# CT-008: --version
def test_version_exit_0():
    r = cli("--version")
    assert r.returncode == 0
    assert b"0.1.0" in r.stdout or b"0.1.0" in r.stderr  # argparse may put on stderr


# CT-003: missing input file → exit 2, error on stderr
def test_encode_missing_file(tmp_path):
    r = cli("encode", "nonexistent_input_file.bin", str(tmp_path / "out.mp4"))
    assert r.returncode == 2
    assert r.stderr != b""
    assert r.stdout == b""


# CT-009: exit code 3 on invalid parameter
def test_encode_invalid_grid_size(tmp_path):
    f = tmp_path / "in.bin"
    f.write_bytes(b"x" * 100)
    r = cli("encode", str(f), str(tmp_path / "out.mp4"), "--grid-size", "99999")
    assert r.returncode == 3
    assert r.stderr != b""


# CT-009: exit code 2 on missing decode input
def test_decode_missing_video(tmp_path):
    r = cli("decode", "no_such_video.mp4", str(tmp_path / "out.bin"))
    assert r.returncode == 2


# CT-009: exit code 5 on bad video for decode
def test_decode_bad_video(tmp_path):
    bad = tmp_path / "bad.mp4"
    bad.write_bytes(b"not a video at all")
    r = cli("decode", str(bad), str(tmp_path / "out.bin"))
    assert r.returncode in (4, 5, 1)  # decoding failed or general
    assert r.stderr != b""
    assert r.stdout == b""


# stderr only for errors, stdout empty
def test_error_goes_to_stderr_not_stdout(tmp_path):
    r = cli("encode", "missing.bin", str(tmp_path / "out.mp4"))
    assert r.returncode != 0
    assert r.stdout == b""
    assert len(r.stderr) > 0


# CT-006: subcommand help
@pytest.mark.parametrize("cmd", ["encode", "decode", "verify", "info"])
def test_subcommand_help(cmd):
    r = cli(cmd, "--help")
    assert r.returncode == 0
