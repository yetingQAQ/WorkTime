# -*- mode: python ; coding: utf-8 -*-

import os


def _normalize_toc_name(entry):
    # TOC entry is usually (dest_name, src_name, typecode).
    return str(entry[0]).replace("\\", "/")


def _prune_qt_payload(toc, drop_software_opengl=False):
    keep_translations = {
        "qt_en.qm",
        "qt_zh_CN.qm",
        "qtbase_en.qm",
        "qtbase_zh_CN.qm",
        "qt_help_en.qm",
        "qt_help_zh_CN.qm",
    }

    dropped_exact = {
        "PyQt6/Qt6/bin/Qt6Pdf.dll",
        "PyQt6/Qt6/plugins/imageformats/qpdf.dll",
        "PyQt6/Qt6/bin/Qt6Svg.dll",
        "PyQt6/Qt6/plugins/iconengines/qsvgicon.dll",
        "PyQt6/Qt6/plugins/imageformats/qsvg.dll",
    }
    if drop_software_opengl:
        dropped_exact.add("PyQt6/Qt6/bin/opengl32sw.dll")

    filtered = []
    for entry in toc:
        name = _normalize_toc_name(entry)

        if name in dropped_exact:
            continue

        if name.startswith("PyQt6/Qt6/translations/"):
            if name.rsplit("/", 1)[-1] not in keep_translations:
                continue

        filtered.append(entry)

    return filtered


spec_dir = SPECPATH
drop_software_opengl = os.environ.get("DROP_SOFTWARE_OPENGL", "0") == "1"

a = Analysis(
    [os.path.join(spec_dir, 'src', 'app.py')],
    pathex=[spec_dir, os.path.join(spec_dir, 'src')],
    binaries=[],
    datas=[(os.path.join(spec_dir, 'icon.ico'), '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt6.QtBluetooth',
        'PyQt6.QtDBus',
        'PyQt6.QtDesigner',
        'PyQt6.QtHelp',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'PyQt6.QtNetwork',
        'PyQt6.QtNfc',
        'PyQt6.QtOpenGL',
        'PyQt6.QtOpenGLWidgets',
        'PyQt6.QtPdf',
        'PyQt6.QtPdfWidgets',
        'PyQt6.QtPositioning',
        'PyQt6.QtPrintSupport',
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtQuick3D',
        'PyQt6.QtQuickWidgets',
        'PyQt6.QtRemoteObjects',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtSpatialAudio',
        'PyQt6.QtSql',
        'PyQt6.QtStateMachine',
        'PyQt6.QtSvg',
        'PyQt6.QtSvgWidgets',
        'PyQt6.QtTest',
        'PyQt6.QtTextToSpeech',
        'PyQt6.QtWebChannel',
        'PyQt6.QtWebSockets',
        'PyQt6.QtXml',
        'tkinter',
        'unittest',
        'email',
        'html',
        'http',
        'urllib',
        'xml',
        'pydoc',
        'doctest',
    ],
    noarchive=False,
)
a.binaries = _prune_qt_payload(a.binaries, drop_software_opengl=drop_software_opengl)
a.datas = _prune_qt_payload(a.datas)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='工作时间进度',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_dir, 'icon.ico'),
)
