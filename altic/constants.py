GROUPS = {
    "BuildRequires(pre)": [],
    "BuildRequires": [],
    "Requires(pre)": [],
    "Provides": [],
    "Conflicts": [],
    "Obsoletes": []
}

STAGES = (
    "prep",
    "setup",
    "build",
    "install",
    "files"
)

# Default values for questions for different templates
TEMPLATES = {
    "python3-module": {
        "group": "Development/Python3",
        "build_arch": "noarch",
        "license": "MIT"
    },
    "rust": {},
    "other": {},
}