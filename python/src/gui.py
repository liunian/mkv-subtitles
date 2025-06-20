# -*- coding: utf-8 -*-
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QCheckBox, QFileDialog, QMessageBox, QLabel, QHBoxLayout
    )
from PySide6.QtCore import Slot
from main import get_subtitle_tracks, extract_all_subtitles, convert_smb_path

class SubtitleExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.mkv_file = None
        self.subtitle_tracks = []
        self.selected_tracks = []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MKV 字幕提取器")
        self.setGeometry(100, 100, 640, 480)
        self.center()

        layout = QVBoxLayout()

        self.select_button = QPushButton("选择 MKV 文件")
        self.select_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.select_button)

        # 添加路径显示标签
        self.label_path = QLabel("未选择文件")
        self.label_path.setWordWrap(True)  # 允许文本换行
        layout.addWidget(self.label_path)

        self.track_list = QListWidget()
        layout.addWidget(self.track_list)

        self.extract_button = QPushButton("提取字幕")
        self.extract_button.clicked.connect(self.extract_subtitles)
        layout.addWidget(self.extract_button)

        self.setLayout(layout)

             # 调用居中方法
        self.center()

    def center(self):
        """将窗口居中到主屏幕"""
        # 获取主屏幕的可用几何区域
        screen = QApplication.primaryScreen().availableGeometry()

        # 获取窗口的几何区域
        window_rect = self.frameGeometry()

        # 计算窗口左上角的目标位置
        x = (screen.width() - window_rect.width()) // 2
        y = (screen.height() - window_rect.height()) // 2

        # 移动窗口到计算位置
        self.move(x, y)

    @Slot()
    def open_file_dialog(self):
        last_dir = self.get_last_dir()
        file_path, _ = QFileDialog.getOpenFileName(self, '选择 MKV 文件', last_dir, 'MKV Files (*.mkv)')
        if file_path:
            self.mkv_file = convert_smb_path(file_path)
            self.label_path.setText(f"已选择文件:\n{self.mkv_file}")
            self.save_last_dir(os.path.dirname(file_path))
            self.display_tracks()
        else:
            self.label_path.setText("")

    def get_last_dir(self):
        last_dir_file = os.path.join(os.path.dirname(__file__), "../.cache/last_dir")
        if os.path.exists(last_dir_file):
            with open(last_dir_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    def save_last_dir(self, dir_path):
        cache_dir = os.path.join(os.path.dirname(__file__), "../.cache")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        last_dir_file = os.path.join(cache_dir, "last_dir")
        with open(last_dir_file, "w", encoding="utf-8") as f:
            f.write(dir_path)

    @Slot()
    def display_tracks(self):
        self.subtitle_tracks = get_subtitle_tracks(self.mkv_file)
        self.track_list.clear()
        for track in self.subtitle_tracks:
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.update_selected_tracks)
            item_label = QLabel(f"Track ID: {track['track_id']}, Format: {track['format']}, Language: {track['language']}")
            item_layout.addWidget(checkbox)
            item_layout.addWidget(item_label)
            item_layout.setContentsMargins(5, 5, 5, 5)  # 调整边距
            item_widget.setLayout(item_layout)

            # 配置布局拉伸因子
            item_layout.setStretch(0, 0)  # 第0个控件（checkbox）拉伸因子为0
            item_layout.setStretch(1, 1)  # 第1个控件（label）拉伸因子为1

            item = QListWidgetItem(self.track_list)
            item.setSizeHint(item_widget.sizeHint())  # 自动调整项高度

            self.track_list.addItem(item)
            self.track_list.setItemWidget(item, item_widget)

    @Slot()
    def update_selected_tracks(self):
        self.selected_tracks = []
        for i in range(self.track_list.count()):
            item = self.track_list.item(i)
            item_widget = self.track_list.itemWidget(item)
            checkbox = item_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                track_id = self.subtitle_tracks[i]['track_id']
                self.selected_tracks.append(track_id)

    @Slot()
    def extract_subtitles(self):
        if not self.selected_tracks:
            QMessageBox.warning(self, '警告', '请选择至少一个字幕轨道')
            return
        tracks_to_extract = [track for track in self.subtitle_tracks if track['track_id'] in self.selected_tracks]
        extract_all_subtitles(self.mkv_file, tracks_to_extract)
        QMessageBox.information(self, '完成', '字幕提取完成')

def main_gui():
    app = QApplication(sys.argv)
    extractor = SubtitleExtractor()
    extractor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main_gui()
