# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# needed for programming: the build folder, and esptool's package data - the
# flasher-stub images it loads at runtime - from the INSTALLED esptool (the
# action installs the clone at the requested tag). Collected generically
# because the layout moved between majors: esptool 4 keeps the stub JSONs in
# esptool/targets/stub_flasher/, esptool 5 in versioned subfolders of it.
added_datas = [('build', 'build')] + collect_data_files('esptool')

# dependencies of esptool 4 and 5, whichever of them are installed (esptool 4
# wants bitstring, ecdsa, six; esptool 5 wants click, rich_click, intelhex,
# yaml; a hidden import that is not installed is a loud error in the build log)
import importlib.util
hidden_imports = [
    module for module in [
        'bitstring',
        'cffi',
        'click',
        'cryptography',
        'ecdsa',
        'esptool',
        'intelhex',
        'pycparser',
        'reedsolo',
        'rich_click',
        'serial',
        'six',
        'yaml',
    ] if importlib.util.find_spec(module) is not None
]

a = Analysis(['programmer.py'],
             pathex=[],
             binaries=[],
             datas=added_datas,
             hiddenimports=hidden_imports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          a.binaries,
          a.zipfiles,
          a.datas,
          name='programmer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tempdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
