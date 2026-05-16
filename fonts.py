"""字体管理模块"""
import pygame
import os
import platform

class FontManager:
    def __init__(self):
        pygame.font.init()
        self.fonts = {}
        self._load_fonts()
    
    def _find_chinese_font(self):
        """查找系统中文字体"""
        system = platform.system()
        
        if system == 'Windows':
            paths = [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
            ]
        elif system == 'Darwin':
            paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
            ]
        else:
            paths = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def _load_fonts(self):
        """加载字体"""
        chinese_font = self._find_chinese_font()
        
        sizes = {
            'title': 28,
            'large': 24,
            'medium': 20,
            'small': 16,
            'tiny': 12,
        }
        
        if chinese_font:
            try:
                for name, size in sizes.items():
                    self.fonts[name] = pygame.font.Font(chinese_font, size)
                return
            except:
                pass
        
        # 回退到系统字体
        for name, size in sizes.items():
            try:
                font = pygame.font.SysFont('arial', size)
                test = font.render('测试', True, (255,255,255))
                if test.get_width() > 10:
                    self.fonts[name] = font
                else:
                    self.fonts[name] = pygame.font.Font(None, size)
            except:
                self.fonts[name] = pygame.font.Font(None, size)
    
    def render(self, text, font_name='medium', color=(255,255,255)):
        """渲染文本"""
        if not isinstance(text, str):
            text = str(text)
        font = self.fonts.get(font_name, self.fonts['medium'])
        return font.render(text, True, color)
    
    def get_font(self, name='medium'):
        return self.fonts.get(name, self.fonts['medium'])