# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],  # Thay thế bằng đường dẫn đến file chính của bạn
    pathex=[''],  # Đường dẫn tới thư mục chứa project của bạn
    binaries=[],
    datas=[  # Thêm tài nguyên (file cần thiết cho ứng dụng, như hình ảnh, file UI, file JSON)
        ('ui/setting', 'ui/setting'),
        ('ui/home', 'ui/home'),
    ],
    hiddenimports=[  # Nếu có thư viện ngoài không được phát hiện tự động, bạn có thể liệt kê ở đây
        'pytube', 'instaloader', 'moviepy.editor', 'requests', 'selenium', 'yt_dlp', 'pytubefix',
        'opencv_python', 'numpy','PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],  # Loại bỏ các thư viện không cần thiết
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
)

# Thêm bước chuyển đổi ứng dụng GUI (cửa sổ không terminal)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Bundle ứng dụng thành executable file
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Nếu muốn loại bỏ binary không cần thiết
    name='social_download_app',  # Đặt tên cho file .exe của bạn
    debug=False,  # Nếu cần debug, chuyển thành True
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Dùng UPX để nén file .exe
    console=False,  # Không hiển thị cửa sổ terminal khi chạy
)

# Tạo file spec hoàn chỉnh
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='social_download_app',  # Đặt tên cho thư mục chứa file .exe
)
