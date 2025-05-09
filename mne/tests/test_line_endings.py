# Authors: The MNE-Python contributors.
# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

import os
import sys
from os import path as op

import pytest

from mne.utils import _get_root_dir

skip_files = (
    # known crlf
    "FreeSurferColorLUT.txt",
    "test_edf_stim_channel.txt",
    "FieldTrip.py",
    "license.txt",
    # part of testing compatibility with older BV formats is testing
    # the line endings and coding schemes used there
    "test_old_layout_latin1_software_filter.vhdr",
    "test_old_layout_latin1_software_filter.vmrk",
    "test_old_layout_latin1_software_filter_longname.vhdr",
    "searchindex.dat",
)


def _assert_line_endings(dir_):
    """Check line endings for a directory."""
    if sys.platform == "win32":
        pytest.skip("Skipping line endings check on Windows")
    report = list()
    good_exts = (
        ".py",
        ".dat",
        ".sel",
        ".lout",
        ".css",
        ".js",
        ".lay",
        ".txt",
        ".elc",
        ".csd",
        ".sfp",
        ".json",
        ".hpts",
        ".vmrk",
        ".vhdr",
        ".head",
        ".eve",
        ".ave",
        ".cov",
        ".label",
    )
    for dirpath, _, filenames in os.walk(dir_):
        for fname in filenames:
            if op.splitext(fname)[1] not in good_exts or fname in skip_files:
                continue
            filename = op.join(dirpath, fname)
            relfilename = op.relpath(filename, dir_)
            try:
                with open(filename, "rb") as fid:
                    text = fid.read().decode("utf-8")
            except UnicodeDecodeError:
                report.append(f"In {relfilename} found non-decodable bytes")
            else:
                crcount = text.count("\r")
                if crcount:
                    lfcount = text.count("\n")
                    report.append(f"In {relfilename} found {crcount}/{lfcount} CR/LF.")
    if len(report) > 0:
        raise AssertionError(
            f"Found {len(report)} files with incorrect endings:\n" + "\n".join(report)
        )


def test_line_endings(tmp_path):
    """Test line endings of mne-python."""
    tempdir = str(tmp_path)
    with open(op.join(tempdir, "foo"), "wb") as fid:
        fid.write("bad\r\ngood\n".encode("ascii"))
    _assert_line_endings(tempdir)
    with open(op.join(tempdir, "bad.py"), "wb") as fid:
        fid.write(b"\x97")
    pytest.raises(AssertionError, _assert_line_endings, tempdir)
    with open(op.join(tempdir, "bad.py"), "wb") as fid:
        fid.write("bad\r\ngood\n".encode("ascii"))
    pytest.raises(AssertionError, _assert_line_endings, tempdir)
    # now check mne
    _assert_line_endings(_get_root_dir())
