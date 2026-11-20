import platform
import subprocess
import unittest

import pytest

from conan.test.utils.tools import TestClient


@pytest.mark.tool("meson")
@pytest.mark.skipif(platform.system() not in ("Darwin", "Windows", "Linux"),
                    reason="Not tested for not mainstream boring operating systems")
class TestMesonBase(unittest.TestCase):
    def setUp(self):
        self.t = TestClient()

    @staticmethod
    def _get_gcc_version():
        try:
            output = subprocess.check_output(["gcc", "-dumpversion"], stderr=subprocess.STDOUT,
                                             text=True).strip()
            return output.split(".")[0]  # Return major version
        except Exception:
            return None

    @staticmethod
    def _get_clang_version():
        try:
            output = subprocess.check_output(["clang", "-dumpversion"], stderr=subprocess.STDOUT,
                                             text=True).strip()
            return output.split(".")[0]  # Return major version
        except Exception:
            return None

    def _check_binary(self):
        # FIXME: Some values are hardcoded to match the CI setup
        host_profile = self.t.get_default_host_profile()
        host_arch = host_profile.settings['arch']
        arch_macro = {
            "gcc": {"armv8": "__aarch64__", "x86_64": "__x86_64__"},
            "msvc": {"armv8": "_M_ARM64", "x86_64": "_M_X64"}
        }
        if platform.system() == "Darwin":
            self.assertIn(f"main {arch_macro['gcc'][host_arch]} defined", self.t.out)
            self.assertIn("main __apple_build_version__", self.t.out)
            clang_version = self._get_clang_version()
            if clang_version:
                self.assertIn(f"main __clang_major__{clang_version}", self.t.out)
            # TODO: check why __clang_minor__ seems to be not defined in XCode 12
            # commented while migrating to XCode12 CI
            # self.assertIn("main __clang_minor__0", self.t.out)
        elif platform.system() == "Windows":
            self.assertIn(f"main {arch_macro['msvc'][host_arch]} defined", self.t.out)
            compiler_version = host_profile.settings.get('compiler.version')
            if compiler_version:
                self.assertIn(f"main _MSC_VER{compiler_version}", self.t.out)
            self.assertIn("main _MSVC_LANG", self.t.out)
        elif platform.system() == "Linux":
            self.assertIn(f"main {arch_macro['gcc'][host_arch]} defined", self.t.out)
            gcc_version = self._get_gcc_version()
            if gcc_version:
                self.assertIn(f"main __GNUC__{gcc_version}", self.t.out)
            else:
                self.assertIn("main __GNUC__", self.t.out)
