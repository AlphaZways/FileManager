"""文件操作模块"""
import os
import subprocess
import platform
import datetime

class FileOperations:
    def __init__(self):
        self.system = platform.system()
    
    def list_directory(self, path):
        """列出目录内容"""
        files = []
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        stat = entry.stat()
                        files.append({
                            'name': entry.name,
                            'path': entry.path,
                            'is_dir': entry.is_dir(),
                            'size': stat.st_size,
                            'modified': datetime.datetime.fromtimestamp(stat.st_mtime),
                            'extension': os.path.splitext(entry.name)[1].lower(),
                        })
                    except:
                        continue
        except PermissionError:
            pass
        
        files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        return files
    
    def open_file(self, path):
        """打开文件"""
        if os.path.isdir(path):
            return 'directory'
            
        ext = os.path.splitext(path)[1].lower()
            
        # 所有文件都用系统默认程序打开（记事本、图片查看器等）
        try:
            if self.system == 'Windows':
                 os.startfile(path)
            elif self.system == 'Darwin':
                subprocess.run(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
            return 'launched'
        except Exception as e:
            print(f"无法打开文件: {e}")
            return 'error'
    
    def read_file(self, path, max_chars=8000):
        """读取文件内容"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'cp1252']
        for enc in encodings:
            try:
                with open(path, 'r', encoding=enc) as f:
                    return f.read(max_chars)
            except UnicodeDecodeError:
                continue
        return None
    
    @staticmethod
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    @staticmethod
    def format_date(dt):
        now = datetime.datetime.now()
        diff = now - dt
        if diff.days == 0:
            return f"今天 {dt.strftime('%H:%M')}"
        elif diff.days == 1:
            return f"昨天 {dt.strftime('%H:%M')}"
        elif diff.days < 7:
            return f"{diff.days}天前"
        return dt.strftime("%Y-%m-%d")