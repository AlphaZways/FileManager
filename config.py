"""配置管理模块"""

"""配置管理模块"""

class Config:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 800
        self.min_width = 800
        self.min_height = 600
        
        self.sidebar_width = 260
        self.item_height = 36
        self.font_size_title = 28
        self.font_size_large = 24
        self.font_size_medium = 20
        self.font_size_small = 16
        self.font_size_tiny = 12
        
        self.max_filename_length = 30
        self.max_preview_chars = 8000
        
        self.current_theme = 'dark'
        self.colors = self._get_theme_colors()
        self.theme_transitioning = False
        self.transition_progress = 1.0  # 0.0 = 旧主题, 1.0 = 新主题
        self.old_colors = self.colors.copy()
            
        # 动画配置
        self.animation_enabled = True
        self.animation_speed = 1.0  # 全局动画速度倍数
        self.hover_animation_duration = 0.15
        self.transition_duration = 0.3
        self.dialog_animation_duration = 0.35
        self.scroll_smoothness = 0.15
        
        # 文件列表动画
        self.file_hover_scale = 1.02
        self.file_hover_lift = 0  # 悬停提升像素
        
        # 侧边栏动画
        self.sidebar_hover_offset = 5  # 悬停时向右偏移
    
    def _get_theme_colors(self):
        if self.current_theme == 'dark':
            return {
                'bg': (25, 28, 40),
                'sidebar': (20, 23, 35),
                'text': (220, 225, 235),
                'text_dim': (150, 155, 165),
                'text_bright': (240, 245, 255),
                'accent': (70, 140, 210),
                'accent_hover': (90, 160, 230),
                'hover': (40, 45, 60),
                'selected': (50, 60, 85),
                'button': (45, 50, 65),
                'button_hover': (55, 62, 80),
                'input_bg': (35, 40, 55),
                'border': (55, 60, 75),
                'scrollbar': (50, 55, 70),
                'scrollbar_thumb': (80, 85, 100),
                'folder': (220, 180, 60),
                'file': (90, 150, 220),
                'image': (200, 100, 100),
                'audio': (100, 200, 100),
                'video': (200, 100, 200),
                'archive': (200, 160, 80),
                'code': (100, 170, 200),
                'document': (160, 140, 200),
                'overlay': (0, 0, 0, 160),
                'shadow': (0, 0, 0, 100),
                'accent_hover': (90, 160, 230),
            }
        else:
            return {
                'bg': (245, 248, 252),
                'sidebar': (235, 240, 248),
                'text': (30, 35, 45),
                'text_dim': (120, 125, 135),
                'text_bright': (10, 15, 25),
                'accent': (60, 170, 110),
                'accent_hover': (80, 190, 130),
                'hover': (225, 235, 230),
                'selected': (200, 220, 210),
                'button': (215, 225, 220),
                'button_hover': (195, 210, 200),
                'input_bg': (238, 244, 248),
                'border': (190, 195, 205),
                'scrollbar': (210, 215, 225),
                'scrollbar_thumb': (160, 165, 175),
                'folder': (220, 170, 50),
                'file': (70, 130, 200),
                'image': (190, 90, 90),
                'audio': (80, 180, 80),
                'video': (180, 80, 180),
                'archive': (180, 140, 60),
                'code': (80, 150, 180),
                'document': (140, 120, 180),
                'overlay': (0, 0, 0, 120),
                'shadow': (0, 0, 0, 60),
                'accent_hover': (80, 190, 130),
            }
    
    def toggle_theme(self):
        self.old_colors = self.colors.copy()
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.colors = self._get_theme_colors()
        self.theme_transitioning = True
        self.transition_progress = 0.0  # 开始过渡


    def get_transition_color(self, color_name):
        """获取过渡中的颜色"""
        if not self.theme_transitioning or self.transition_progress >= 1.0:
            return self.colors.get(color_name, (255, 255, 255))
        
        old_color = self.old_colors.get(color_name, (255, 255, 255))
        new_color = self.colors.get(color_name, (255, 255, 255))
        
        t = self.transition_progress
        # 使用缓动函数让过渡更平滑
        t = t * t * (3 - 2 * t)  # smoothstep
        
        return tuple(
            int(old_color[i] + (new_color[i] - old_color[i]) * t)
            for i in range(min(len(old_color), len(new_color)))
        )

    def _get_theme_colors(self):
        if self.current_theme == 'dark':
            return {
                'bg': (25, 28, 40),
                'sidebar': (20, 23, 35),
                'text': (220, 225, 235),
                'text_dim': (150, 155, 165),
                'text_bright': (240, 245, 255),
                'accent': (70, 140, 210),
                'accent_hover': (90, 160, 230),
                'hover': (40, 45, 60),
                'selected': (50, 60, 85),
                'button': (45, 50, 65),
                'button_hover': (55, 62, 80),
                'input_bg': (35, 40, 55),
                'border': (55, 60, 75),
                'scrollbar': (50, 55, 70),
                'scrollbar_thumb': (80, 85, 100),
                'folder': (220, 180, 60),
                'file': (90, 150, 220),
                'image': (200, 100, 100),
                'audio': (100, 200, 100),
                'video': (200, 100, 200),
                'archive': (200, 160, 80),
                'code': (100, 170, 200),
                'document': (160, 140, 200),
                'overlay': (0, 0, 0, 160),
                'shadow': (0, 0, 0, 100),
            }
        else:
            return {
                'bg': (245, 248, 252),
                'sidebar': (235, 240, 248),
                'text': (30, 35, 45),
                'text_dim': (120, 125, 135),
                'text_bright': (10, 15, 25),
                'accent': (60, 170, 110),
                'accent_hover': (80, 190, 130),
                'hover': (225, 235, 230),
                'selected': (200, 220, 210),
                'button': (215, 225, 220),
                'button_hover': (195, 210, 200),
                'input_bg': (238, 244, 248),
                'border': (190, 195, 205),
                'scrollbar': (210, 215, 225),
                'scrollbar_thumb': (160, 165, 175),
                'folder': (220, 170, 50),
                'file': (70, 130, 200),
                'image': (190, 90, 90),
                'audio': (80, 180, 80),
                'video': (180, 80, 180),
                'archive': (180, 140, 60),
                'code': (80, 150, 180),
                'document': (140, 120, 180),
                'overlay': (0, 0, 0, 120),
                'shadow': (0, 0, 0, 60),
            }
    
    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.colors = self._get_theme_colors()