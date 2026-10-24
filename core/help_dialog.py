from PySide6.QtWidgets import (QDialog, QVBoxLayout, QScrollArea, QWidget, QGroupBox, 
                               QLabel, QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt

from core.config import config
from core.styles import get_dialog_style, get_scroll_area_style
from core.widgets import BackgroundWidget, load_background_image


class HelpDialog(QDialog):
    """帮助对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("帮助")
        self.setModal(False)  # 改为非模态，允许用户与其他窗口交互
        self.setFixedSize(850, 600)
        
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setStyleSheet(get_dialog_style(config.theme))

        self.background_pixmap = None
        self._load_background_image()

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.container_widget = BackgroundWidget(self.background_pixmap, config.theme)
        self.container_widget.setObjectName("dialogContainer")
        container_layout = QVBoxLayout(self.container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        main_layout.addWidget(self.container_widget)
        
        from core.custom_title_bar import CustomTitleBar
        self.title_bar = CustomTitleBar(self, show_theme_toggle=False)
        container_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        container_layout.addWidget(content_widget)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet(get_scroll_area_style(config.theme))
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("QWidget { background: transparent; }")
        scroll_layout = QVBoxLayout(scroll_content)

        help_group = QGroupBox("使用指南")
        help_group.setStyleSheet("QGroupBox { background: transparent; }")
        help_layout = QVBoxLayout(help_group)

        help_text = QLabel(
            "<h3>鸣潮成就管理器 - 使用帮助</h3>"
            
            "<p><b>🌟 软件使用指南</b></p>"
            "<p style='margin-left: 20px;'><span style='color: #3498db;'><b>💡 简单来说，这个工具是干嘛的？</b></span><br>"
            "这是一个帮你记录和管理《鸣潮》游戏成就进度的工具。你可以用它来：<br>"
            "• ✅ 标记已完成的成就，包括已完成、未完成、已占用(多选一成就)、暂不可获取(永远不会抽的角色的延奏成就或1.2追月节成就等等)<br>"
            "• 📊 查看成就完成进度统计图表<br>"
            "• 👥 支持多个用户，每个用户可以独立记录自己的进度<br>"
            "• ❣️ 美化的软件界面，包含头像、立绘、背景图（使用需在下载页面下载resources.zip并解压，将文件夹(忽略json文件)复制到该软件的resources文件夹内）</p>"
            
            
            "<p><b>1. 成就内容可以自己改</b></p>"
            "<p style='margin-left: 20px;'>Wiki 上的成就不需要登录就能爬取。<br>"
            "如果某条写错了、漏了，或者多了一条不存在的成就：<br>"
            "• 点成就管理里的<b>新增成就</b>补上漏掉的条目<br>"
            "• 在表格里<b>右键</b>某条成就，选择<b>编辑</b>或<b>删除</b><br>"
            "改过或删掉的内容会保留。之后再爬取或启动时自动同步，只会补充你本地还没有的成就，不会把你的修改覆盖掉。</p>"
            
            "<p><b>2. 数据说明</b></p>"
            "<p style='margin-left: 20px;'><span style='color: #3498db;'><b>📊 内置数据：</b></span><br>"
            "• 程序已经内置了1.0-2.8版本的完整成就数据，共764条<br>"
            "<span style='color: #3498db;'><b>🔄 更新数据：</b></span><br>"
            "• 当游戏更新新版本时，可以通过三种方式获取最新成就数据：<br>"
            "  1. <b>数据爬取-B站UP主</b>：通过b站up主：<b>小白游戏导航</b>的视频按照<b>导出范本</b>的格式自行编辑后，导入Excel，确认覆盖（最快）<br>"
            "  2. <b>数据爬取</b>：无需登录。等 Wiki 有新版本数据后，输入版本号，开始爬取，确认添加<br>"
            "  3. <b>数据爬取-下载页面</b>：是我通过b站up主：<b>小白游戏导航</b>的视频按照范本格式整理的，导入Excel，确认覆盖（不保证每次都有）</p>"
            
            "<p><b>3. 状态列操作说明</b></p>"
            "<p style='margin-left: 20px;'>在成就管理标签页的表格中:<br>"
            "• <b>单击</b>状态列：在<span style='color: #27ae60;'>已完成</span>和<span style='color: #95a5a6;'>未完成</span>之间切换<br>"
            "• <b>长按</b>状态列(按住1秒)：切换为<span style='color: #e67e22;'>暂不可获取</span>状态，再次单击恢复为未完成状态<br>"
            "• 多选一成就，点击成就组内任一成就，会将其他成就改为 已占用 状态<br>"
            "• 单击第一分类或第二分类，可更改所属分类<br>"
            "• <b>右键</b>一行可编辑名称、描述、奖励、版本、隐藏状态和分类，或删除该成就<br>"
            "• <b>新增成就</b>用于补上 Wiki 里没有的条目</p>"
            
            "<p><b>4. 爬虫使用说明与数据版本管理（进阶功能）</b></p>"
            "<p style='margin-left: 20px;'><span style='color: #e74c3c;'><b>⚠️ 重要提示：</b></span><br>"
            "• 爬取和启动同步只会补充本地没有的成就，不会删除你改过或自行添加的条目<br>"
            "• Wiki 上多出来的错误成就，请在成就管理里右键删除<br>"
            "• 建议通过点击<b>打开WIKI</b>按钮确认有新版本数据后再爬取<br><br>"
            "<span style='color: #3498db;'><b>🚀 爬虫功能使用步骤：</b></span><br>"
            "爬虫功能<b>仅支持单个版本</b>的数据爬取，无需登录。<br>"
            "① 输入要爬取的版本(如：3.0)<br>"
            "② 点击开始爬取按钮<br>"
            "③ 等待爬取完成后点击<b>确认添加</b>保存数据<br><br>"
            "<span style='color: #3498db;'><b>💾 缓存机制：</b></span><br>"
            "• 首次爬取时会将网页数据保存到本地缓存(resources/achievement_cache.json)<br>"
            "• 已有缓存时会比对远端更新时间，有变化才覆盖本地缓存<br>"
            "• 点击<b>清除缓存</b>按钮可删除本地缓存文件，下次爬取将重新获取最新数据<br>"
            "• 点击<b>打开WIKI</b>按钮可在浏览器中查看库街区Wiki成就页面是否有新版本成就数据</p>"
            
            "<p><b>5. 设置-分类管理说明</b></p>"
            "• 可以拖动表格行来改变第一分类、第二分类的排序，保持和游戏内排序一致<br>"
            "• 保存设置后会自动重新编码，自动修改所有用户存档数据来适配新排序，不会导致状态数据丢失<br>"
            "• 爬取数据遇到游戏新增的第一二分类时会自动保存在分类配置中，无需手动管理<br>"
            "• 确认覆盖也会自动重新编码所有用户数据来保证数据一致性</p>"
            
            "<p><b>6. 设置-多选一管理说明</b></p>"
            "• 点击添加组，再点击组名称表格中的内容<br>"
            "• 点击添加成就，搜索多选一的成就名称<br>"
            "• 勾选后，点击确定，点击保存<br>"
            "• 在成就管理-获取类型中筛选<b>多选一</b>来管理多选一成就完成状态</p>"
            
            "<p><b>7. 设置-版本管理说明</b></p>"
            "• 仅仅是某一版本成就数据有误时，用来删除当前版本数据的功能，通常可忽略<br>"
            "• 删除时，会自动导出所有用户的当前删除版本的成就数据</p>"
            
            "<p><b>8. 角色头像和立绘</b></p>"
            "<p style='margin-left: 20px;'>不需要自己去 Wiki 保存图片。<br>"
            "点击主窗口左上角头像，再点击<b>同步角色形象</b>。<br>"
            "程序会下载头像到 <code>resources\\profile</code>，下载编队立绘到 <code>resources\\characters</code>。<br>"
            "两边都用角色名做文件名，切换头像时会显示对应立绘。已经存在的同名图片不会被覆盖。</p>"
            
            "<p style='margin-left: 20px;'><span style='color: #27ae60;'><b>🎉 总结：小白用户使用流程</b></span><br>"
            "1. 打开程序 → 直接开始使用内置的1.0-2.8成就数据<br>"
            "2. 在成就管理页面标记你的完成状态<br>"
            "3. 游戏更新新版本时 → 等待别人整理好的Excel数据（按照范本格式自行整理） → 数据爬取页面 → 导入Excel → 确认覆盖<br>"
            "4. 不需要了解 JSON，也不需要登录 Wiki，开箱即用。</p>"
        )
        help_text.setWordWrap(True)
        help_text.setTextFormat(Qt.TextFormat.RichText)
        help_text.setOpenExternalLinks(True)
        
        # 使用统一的帮助文本样式
        from core.styles import get_help_text_style
        help_text.setStyleSheet(get_help_text_style(config.theme))
        help_layout.addWidget(help_text)

        scroll_layout.addWidget(help_group)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def check_for_updates(self):
        """检查更新"""
        # 获取父窗口（主窗口）
        parent = self.parent()
        if parent and hasattr(parent, 'check_for_updates_manual'):
            parent.check_for_updates_manual()
    
    def _load_background_image(self):
        """加载背景图片"""
        self.background_pixmap = load_background_image(config.theme)
