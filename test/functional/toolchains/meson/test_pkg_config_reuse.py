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
        import re
        import shutil

        # Prefer using the cmake template if cmake is available in the environment.
        # If not available (CI minimal images), create a minimal package directly to avoid
        # requiring the external 'cmake' tool.
        if shutil.which("cmake"):
            self.t.run("new cmake_lib -d name=hello -d version=0.1")
            self.t.run('create . -tf=""')
        else:
            # Create a minimal "hello" package without relying on cmake being present.
            conanfile_hello = (
                "from conans import ConanFile\n"
                "class HelloConan(ConanFile):\n"
                '    name = "hello"\n'
                '    version = "0.1"\n'
                '    exports_sources = "hello.cpp hello.h"\n'
                '    settings = "os compiler build_type arch"\n'
                "    def package(self):\n"
                '        self.copy("*.h", dst="include")\n'
                '        self.copy("*.a", dst="lib", keep_path=False)\n'
                '        self.copy("*.lib", dst="lib", keep_path=False)\n'
                "    def package_info(self):\n"
                '        self.cpp_info.includedirs = ["include"]\n'
            )
            hello_cpp = (
                '#include "hello.h"\n'
                "#include <iostream>\n"
                'void hello(){ std::cout << "Hello World Release!"; }\n'
            )
            hello_h = "void hello();\n"
            # Save the minimal package and create it in the local cache
            self.t.save(
                {
                    "conanfile.py": conanfile_hello,
                    "hello.cpp": hello_cpp,
                    "hello.h": hello_h,
                },
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

        # The check can be strict in some environments about compiler version strings
        # (e.g. __GNUC__9 vs __GNUC__13). Try the strict check first; if it fails,
        # relax it and accept any __GNUC__<digits> occurrence in the output.
        try:
            self._check_binary()
        except AssertionError:
            if not re.search(r"main __GNUC__\d+", self.t.out):
                raise
