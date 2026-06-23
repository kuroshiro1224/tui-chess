from setuptools import setup, find_packages

setup(
    name='kurochess',
    version='1.0.0',
    packages=find_packages(), # Tự động tìm các package trong dự án
    install_requires=[
        'colorama',
        'chess'
    ],
    entry_points={
        'console_scripts': [
            # kurochess là lệnh bạn sẽ gõ trên terminal
            # src.main:main nghĩa là chạy hàm main() bên trong file main.py (nằm trong thư mục src)
            # (Nếu main.py của bạn nằm ngay ở thư mục gốc, đổi thành 'main:main')
            'kurochess=src.main:main', 
        ],
    },
)