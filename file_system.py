"""文件系统核心"""
import os
from file_ops import FileOperations

class FileSystem:
    def __init__(self, config):
        self.config = config
        self.ops = FileOperations()
        
        self.current_path = os.path.expanduser("~")
        self.files = []
        self.selected_file = None
        
        self.scroll_offset = 0
        self.target_scroll = 0
        self.max_scroll = 0
        
        self.preview_active = False
        self.preview_content = ""
        self.preview_file_path = None
        
        self.settings_active = False
        self.settings_file = None
        
        self.history = [self.current_path]
        self.history_index = 0
        
        self.associations = {}
        self.refresh()
    
    def refresh(self):
        self.files = self.ops.list_directory(self.current_path)
        total_h = len(self.files) * self.config.item_height
        visible_h = self.config.screen_height - 130
        self.max_scroll = max(0, total_h - visible_h)
        self.selected_file = None
    
    def navigate(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.history = self.history[:self.history_index+1]
            self.history.append(path)
            self.history_index = len(self.history) - 1
            self.scroll_offset = 0
            self.target_scroll = 0
            self.refresh()
            return True
        return False
    
    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            return self.navigate(parent)
        return False
    
    def go_home(self):
        return self.navigate(os.path.expanduser("~"))
    
    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self.scroll_offset = 0
            self.target_scroll = 0
            self.refresh()
            return True
        return False
    
    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            self.scroll_offset = 0
            self.target_scroll = 0
            self.refresh()
            return True
        return False
    
    def open_selected(self):
        if not self.selected_file:
            return
        
        path = self.selected_file
        result = self.ops.open_file(path)
        
        if result == 'directory':
            self.navigate(path)
        elif result == 'preview':
            content = self.ops.read_file(path)
            if content is not None:
                self.preview_content = content
                self.preview_active = True
                self.preview_file_path = path
    
    def close_preview(self):
        self.preview_active = False
        self.preview_content = ""
        self.preview_file_path = None
    
    def close_settings(self):
        self.settings_active = False
        self.settings_file = None
    
    def get_quick_paths(self):
        """获取快速访问路径"""
        home = os.path.expanduser("~")
        paths = [
            ("文档", os.path.join(home, "Documents")),
            ("下载", os.path.join(home, "Downloads")),
            ("桌面", os.path.join(home, "Desktop")),
            ("图片", os.path.join(home, "Pictures")),
            ("音乐", os.path.join(home, "Music")),
            ("视频", os.path.join(home, "Videos")),
        ]
        
        result = []
        for name, path in paths:
            if os.path.exists(path):
                result.append((name, path))
            else:
                print(f"快速访问路径不存在: {path}")
        
        return result