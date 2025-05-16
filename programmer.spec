# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_system_data_files

block_cipher = None

# needed for programming
added_datas = [
    ('esptool/flasher_stub/*.c', './flasher_stub/'),
    ('esptool/flasher_stub/*.py', './flasher_stub/'),
    ('esptool/flasher_stub/ld/*.ld', './flasher_stub/ld/'),
    ('esptool/flasher_stub/include/*.h', './flasher_stub/include/'),
    ('esptool/esptool/*.py', './esptool/'),
    ('esptool/esptool/targets/*.py', './esptool/targets/'),
    ('esptool/esptool/targets/stub_flasher/*.json', './esptool/targets/stub_flasher/')
]

added_datas += collect_system_data_files('build', 'build')

print("added_datas:", added_datas)

# pulled from the requirements.txt
hidden_imports = [
    'bitstring',
    'cffi',
    'cryptography',
    'ecdsa',
    'esptool',
    'pycparser',
    'pyserial',
    'reedsolo',
    'six'
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
