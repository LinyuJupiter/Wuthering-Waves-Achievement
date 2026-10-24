import ctypes
import os
import subprocess
import sys


def _is_admin():
    """当前进程是否已经拿到管理员权限。"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _is_compiled():
    """Nuitka 打包后的可执行文件。"""
    return "__compiled__" in globals() or getattr(sys, "frozen", False)


def ensure_admin():
    """截图和 OCR 需要管理员权限。未提权时重新启动自身并退出当前进程。"""
    if sys.platform != "win32" or _is_admin():
        return

    if _is_compiled():
        executable = sys.executable
        params = subprocess.list2cmdline(sys.argv[1:])
    else:
        executable = sys.executable
        pythonw = os.path.join(os.path.dirname(executable), "pythonw.exe")
        if os.path.basename(executable).lower() == "python.exe" and os.path.isfile(pythonw):
            executable = pythonw
        params = subprocess.list2cmdline(sys.argv)

    shell32 = ctypes.windll.shell32
    shell32.ShellExecuteW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_int,
    ]
    shell32.ShellExecuteW.restype = ctypes.c_void_p
    result = shell32.ShellExecuteW(
        None, "runas", executable, params or None, os.getcwd(), 1
    )
    if not result or result <= 32:
        ctypes.windll.user32.MessageBoxW(
            None,
            "未获得管理员权限，无法截图识别游戏界面。",
            "鸣潮成就管理器",
            0x10,
        )
    raise SystemExit(0)


if __name__ == "__main__":
    ensure_admin()

import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from core.logger import setup_logging
from core.styles import get_icon
from version import VERSION

setup_logging()
logger = logging.getLogger(__name__)

def setup_application():
    """设置应用程序基本属性"""
    app = QApplication(sys.argv)
    app.setApplicationName("鸣潮成就管理器")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("鸣潮成就工具")
    
    # 设置全局默认字体为微软雅黑
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 设置窗口图标
    icon = get_icon("logo")
    if not icon.isNull():
        app.setWindowIcon(icon)
    
    return app


def main():
    """主函数"""
    try:
        if sys.platform == "win32":
            logger.info("已使用管理员权限启动")
        logger.info("正在创建应用实例...")
        # 创建应用实例
        app = setup_application()
        logger.info("应用实例创建完成")

        logger.info("正在导入TemplateMainWindow...")
        from core.main_window import TemplateMainWindow
        logger.info("TemplateMainWindow导入完成")

        logger.info("正在创建主窗口...")
        # 创建主窗口
        main_window = TemplateMainWindow()
        logger.info("主窗口创建完成")

        logger.info("正在显示主窗口...")
        # 直接显示窗口（不使用延迟）
        main_window.show()
        logger.info("主窗口显示完成")

        logger.info("应用启动成功！")
        # 运行应用
        sys.exit(app.exec())
    except Exception as e:
        logger.error("启动应用时发生错误: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()