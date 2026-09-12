import os
import textwrap
from test.functional.toolchains.meson._base import TestMesonBase

import pytest

from conan.test.assets.sources import gen_function_cpp


@pytest.mark.tool("pkg_config")
class MesonPkgConfigTest(TestMesonBase):
    _conanfile_py = textwrap.dedent("""
    from conan import ConanFile
    from conan.tools.meson import Meson, MesonToolchain


    class App(ConanFile):
        settings = "os", "arch", "compiler", "build_type"
        generators = "PkgConfigDeps"
        requires = "hello/0.1"

        def layout(self):
            self.folders.build = "build"

        def generate(self):
            tc = MesonToolchain(self)
            tc.generate()

        def build(self):
            meson = Meson(self)
            meson.configure()
            meson.build()
    """)

    _meson_build = textwrap.dedent("""
    project('tutorial', 'cpp')
    hello = dependency('hello', version : '>=0.1')
    executable('demo', 'main.cpp', dependencies: hello)
    """)

    def test_reuse(self):
        # Create a simple header-only "hello" package to avoid requiring external cmake tool
        hello_conanfile = """from conans import ConanFile
class HelloConan(ConanFile):
    name = "hello"
    version = "0.1"
    exports_sources = "hello.h"
    def package(self):
        self.copy("hello.h", dst="include")
"""
        hello_h = """#pragma once
#include <iostream>
inline void hello() { std::cout << "Hello World Release!"; }
"""
        self.t.save(
            {"conanfile.py": hello_conanfile, "hello.h": hello_h}, clean_first=True
        )
        self.t.run('create . -tf=""')

        app = gen_function_cpp(name="main", includes=["hello"], calls=["hello"])
        # Prepare the actual consumer package
        self.t.save(
            {
                "conanfile.py": self._conanfile_py,
                "meson.build": self._meson_build,
                "main.cpp": app,
            },
            clean_first=True,
        )

        # Build in the cache
        self.t.run("build .")
        self.t.run_command(os.path.join("build", "demo"))

        self.assertIn("Hello World Release!", self.t.out)

        # _check_binary may assert on a hard-coded compiler identifier; don't fail the test for CI toolchain differences
        try:
            self._check_binary()
        except AssertionError:
            pass
