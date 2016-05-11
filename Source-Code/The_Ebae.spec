# -*- mode: python -*-

block_cipher = None

options = [('windowed', None, 'OPTION')]

a = Analysis(['The_Ebae.py'],
             pathex=['C:\\Users\\jumpo_000\\Documents\\Programming\\Python\\Ebay Scraper\\Ebay'],
             binaries=None,
             datas=[('.\\Price-Tag.ico', '.'), ('.\\SadSponge.gif', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          options,
          exclude_binaries=True,
          name='The_Ebae',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon="C:\\Users\\jumpo_000\\Documents\\Programming\\Python\\Ebay Scraper\\Ebay\\Price-Tag.ico" )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='The_Ebae')
