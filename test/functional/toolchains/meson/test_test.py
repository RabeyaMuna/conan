import os
import textwrap
from test.functional.toolchains.meson._base import TestMesonBase

import pytest

from conan.test.assets.sources import gen_function_cpp


@pytest.mark.tool("pkg_config")
class MesonTest(TestMesonBase):
    _test_package_meson_build = textwrap.dedent("""
        project('test_package', 'cpp')
        hello = dependency('hello', version : '>=0.1')
        test_package = executable('test_package', 'test_package.cpp', dependencies: hello)
        test('test package', test_package)
        """)

    _test_package_conanfile_py = textwrap.dedent("""
        import os
        from conan import ConanFile
        from conan.tools.meson import Meson, MesonToolchain


        class TestConan(ConanFile):
            settings = "os", "compiler", "build_type", "arch"
            generators = "PkgConfigDeps"

            def requirements(self):
                self.requires(self.tested_reference_str)

            def layout(self):
                self.folders.build = "build"

            def generate(self):
                tc = MesonToolchain(self)
                tc.generate()

            def build(self):
                meson = Meson(self)
                meson.configure()
                meson.build()

            def test(self):
                meson = Meson(self)
                meson.configure()
                meson.test()
        """)

    def test_reuse(self):
        # Avoid using the 'conan new cmake_lib' generator which requires an external 'cmake' tool
        # Create a minimal header-only "hello" package so CI doesn't need cmake installed
        hello_conanfile = """from conans import ConanFile

class HelloConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "include/*"

    def package(self):
        self.copy("*.h", dst="include", src="include")

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
"""

        hello_header = """#pragma once
inline void hello() {}
"""

        # Save the header-only package in the current directory
        self.t.save(
            {
                "conanfile.py": hello_conanfile,
                os.path.join("include", "hello.h"): hello_header,
            }
        )

        test_package_cpp = gen_function_cpp(
            name="main", includes=["hello"], calls=["hello"]
        )

        self.t.save(
            {
                os.path.join(
                    "test_package", "conanfile.py"
                ): self._test_package_conanfile_py,
                os.path.join(
                    "test_package", "meson.build"
                ): self._test_package_meson_build,
                os.path.join("test_package", "test_package.cpp"): test_package_cpp,
            }
        )

        self.t.run("create . --name=hello --version=0.1")

        self._check_binary()
