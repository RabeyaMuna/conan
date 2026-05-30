# User-defined tool locations override
# This file is used to disable tools that are not available in the CI environment

tools_locations = {
    # Disable tools that are not available in the CI environment
    "cmake": {"disabled": True},
    "bazel": {"disabled": True},
    "qbs": {"disabled": True},
    "scons": {"disabled": True},
    "emcc": {"disabled": True},
    "premake": {"disabled": True},
}
