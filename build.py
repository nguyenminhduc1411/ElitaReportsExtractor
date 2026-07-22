import os
import subprocess

from version import APP_VERSION
major, minor, patch = APP_VERSION.split(".")

content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major},{minor},{patch},0),
    prodvers=({major},{minor},{patch},0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0,0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'Johnson & Johnson Vision'),
          StringStruct('FileDescription', 'Elita Reports Extractor'),
          StringStruct('FileVersion', '{APP_VERSION}'),
          StringStruct('InternalName', 'Elita Reports Extractor'),
          StringStruct('OriginalFilename', 'Elita Reports Extractor.exe'),
          StringStruct('ProductName', 'Elita Reports Extractor'),
          StringStruct('ProductVersion', '{APP_VERSION}'),
          StringStruct('LegalCopyright', '© 2026 Nguyen Minh Duc'),
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""

with open("version_info.txt", "w", encoding="utf-8") as f:
    f.write(content)

print("Generated version_info.txt")

print(f"Building version {APP_VERSION}")

subprocess.run(
    ["pyinstaller", "--noconfirm", "main.spec"],
    check=True
)

os.environ["APP_VERSION"] = APP_VERSION

ISCC = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

subprocess.run(
    [ISCC, "installer.iss"],
    check=True
)

print("Build completed successfully.")