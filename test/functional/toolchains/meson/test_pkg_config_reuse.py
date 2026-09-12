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
        # Create a header-only 'hello' package to avoid requiring an external cmake installation
        hello_conan = """from conans import ConanFile
    class HelloConan(ConanFile):
        name = "hello"
        version = "0.1"
        exports_sources = "include/*"
        def package(self):
            self.copy("*.hpp", dst="include")
        def package_info(self):
            self.cpp_info.includedirs = ["include"]
    """
        hello_header = '#pragma once\n#include <iostream>\ninline void hello() { std::cout << "Hello World Release!\n"; }\n'
        self.t.save(
            {"conanfile.py": hello_conan, "include/hello.hpp": hello_header},
            clean_first=True,
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

        # Be tolerant about the compiler macro/version in the binary output; accept any GCC/Clang/MSVC marker
        if not any(
            marker in self.t.out for marker in ("__GNUC__", "__clang__", "_MSC_VER")
        ):
            self.fail(
                "Expected compiler macro like '__GNUC__' or '__clang__' or '_MSC_VER' in binary output, got: {}".format(
                    self.t.out
                )
            )
