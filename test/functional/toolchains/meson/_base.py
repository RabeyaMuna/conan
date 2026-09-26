import platform
import subprocess
import unittest

import pytest

from conan.test.utils.tools import TestClient


def _get_gcc_major_version():
    """Get the GCC major version from the environment."""
    try:
        result = subprocess.run(['gcc', '-dumpversion'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        version = result.stdout.strip()
        major = version.split('.')[0]
        return major
    except (subprocess.SubprocessError, FileNotFoundError, IndexError, ValueError):
        return "9"  # fallback to default


@pytest.mark.tool("meson")
@pytest.mark.skipif(platform.system() not in ("Darwin", "Windows", "Linux"),
                    reason="Not tested for not mainstream boring operating systems")
class TestMesonBase(unittest.TestCase):
    def setUp(self):
        self.t = TestClient()

    def _check_binary(self):
        # FIXME: Some values are hardcoded to match the CI setup
        host_arch = self.t.get_default_host_profile().settings['arch']
        arch_macro = {
            "gcc": {"armv8": "__aarch64__", "x86_64": "__x86_64__"},
            "msvc": {"armv8": "_M_ARM64", "x86_64": "_M_X64"}
        }
        if platform.system() == "Darwin":
            self.assertIn(f"main {arch_macro['gcc'][host_arch]} defined", self.t.out)
            self.assertIn("main __apple_build_version__", self.t.out)
            self.assertIn("main __clang_major__15", self.t.out)
            # TODO: check why __clang_minor__ seems to be not defined in XCode 12
            # commented while migrating to XCode12 CI
            # self.assertIn("main __clang_minor__0", self.t.out)
        elif platform.system() == "Windows":
            self.assertIn(f"main {arch_macro['msvc'][host_arch]} defined", self.t.out)
            self.assertIn("main _MSC_VER19", self.t.out)
            self.assertIn("main _MSVC_LANG2014", self.t.out)
        elif platform.system() == "Linux":
            self.assertIn(f"main {arch_macro['gcc'][host_arch]} defined", self.t.out)
            gcc_major = _get_gcc_major_version()
            self.assertIn(f"main __GNUC__{gcc_major}", self.t.out)
