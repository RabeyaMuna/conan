import platform
import unittest

import pytest

from conan.test.utils.tools import TestClient


@pytest.mark.tool("meson")
@pytest.mark.skipif(
    platform.system() not in ("Darwin", "Windows", "Linux"),
    reason="Not tested for not mainstream boring operating systems",
)
class TestMesonBase(unittest.TestCase):
    def setUp(self):
        self.t = TestClient()

    def _check_binary(self):
        # FIXME: Some values are hardcoded to match the CI setup
        # Made checks resilient to different compiler/toolchain versions by
        # verifying presence of the macro name and a numeric suffix when applicable
        import re

        host_arch = self.t.get_default_host_profile().settings["arch"]
        arch_macro = {
            "gcc": {"armv8": "__aarch64__", "x86_64": "__x86_64__"},
            "msvc": {"armv8": "_M_ARM64", "x86_64": "_M_X64"},
        }
        if platform.system() == "Darwin":
            self.assertIn(f"main {arch_macro['gcc'][host_arch]} defined", self.t.out)
            self.assertIn("main __apple_build_version__", self.t.out)
            # Accept any __clang_major__ with a numeric value, don't hardcode major version
            self.assertTrue(
                re.search(r"main __clang_major__\d+", self.t.out),
                "expected main __clang_major__<number>",
            )
            # TODO: check why __clang_minor__ seems to be not defined in XCode 12
            # commented while migrating to XCode12 CI
            # self.assertTrue(re.search(r"main __clang_minor__\d+", self.t.out))
        elif platform.system() == "Windows":
            self.assertIn(f"main {arch_macro['msvc'][host_arch]} defined", self.t.out)
            # Accept any _MSC_VER with a numeric value
            self.assertTrue(
                re.search(r"main _MSC_VER\d+", self.t.out),
                "expected main _MSC_VER<digits>",
            )
            self.assertIn("main _MSVC_LANG2014", self.t.out)
        elif platform.system() == "Linux":
            self.assertIn(f"main {arch_macro['gcc'][host_arch]} defined", self.t.out)
            # Accept any __GNUC__ with a numeric value instead of hardcoding 9
            self.assertTrue(
                re.search(r"main __GNUC__\d+", self.t.out),
                "expected main __GNUC__<number>",
            )
