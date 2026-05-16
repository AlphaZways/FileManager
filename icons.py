"""纯图形图标系统 - 完全不使用emoji"""
import pygame
import math

class Icons:
    """使用纯几何图形绘制图标"""
    
    @staticmethod
    def draw(surface, name, x, y, size, color):
        """绘制指定图标"""
        drawer = getattr(Icons, f'_draw_{name}', Icons._draw_default)
        drawer(surface, x, y, size, color)
    
    @staticmethod
    def _draw_home(surface, x, y, s, c):
        """房子图标"""
        # 屋顶三角形
        pts = [(x+s//2, y+2), (x+3, y+s//2), (x+s-3, y+s//2)]
        pygame.draw.polygon(surface, c, pts)
        # 墙体
        pygame.draw.rect(surface, c, (x+5, y+s//2, s-10, s//2-2))
        # 门
        dc = Icons._darken(c, 60)
        pygame.draw.rect(surface, dc, (x+s//3, y+s*2//3, s//3, s//3-2))
    
    @staticmethod
    def _draw_folder(surface, x, y, s, c):
        """文件夹图标"""
        # 主体
        pygame.draw.rect(surface, c, (x+2, y+4, s-4, s-6), border_radius=2)
        # 标签
        pygame.draw.rect(surface, c, (x+2, y+1, s//2, 5), border_top_left_radius=2, border_top_right_radius=2)
        # 高光
        lc = Icons._lighten(c, 40)
        pygame.draw.rect(surface, lc, (x+5, y+7, s//3, s//4), border_radius=1)
    
    @staticmethod
    def _draw_file(surface, x, y, s, c):
        """文件图标"""
        # 主体
        pygame.draw.rect(surface, c, (x+3, y+1, s-5, s-2), border_radius=2)
        # 折角
        dc = Icons._darken(c, 40)
        pts = [(x+s-7, y+1), (x+s-2, y+7), (x+s-7, y+7)]
        pygame.draw.polygon(surface, dc, pts)
        # 文本线
        lc = Icons._lighten(c, 50)
        for i, ly in enumerate([y+s//3, y+s//2, y+s*2//3]):
            lw = s//2 + i*2
            pygame.draw.line(surface, lc, (x+6, ly), (x+6+lw, ly), 1)
    
    @staticmethod
    def _draw_up(surface, x, y, s, c):
        """向上箭头"""
        # 箭头
        pts = [(x+s//2, y+3), (x+4, y+s-5), (x+s-4, y+s-5)]
        pygame.draw.polygon(surface, c, pts)
        # 杆
        sw = max(2, s//8)
        pygame.draw.rect(surface, c, (x+s//2-sw//2, y+5, sw, s-8))
    
    @staticmethod
    def _draw_refresh(surface, x, y, s, c):
        """刷新图标"""
        cx, cy = x+s//2, y+s//2
        r = s//2 - 2
        # 弧形
        pts = []
        for a in range(60, 300, 3):
            rad = math.radians(a)
            pts.append((cx + r*math.cos(rad), cy + r*math.sin(rad)))
        if len(pts) > 1:
            pygame.draw.lines(surface, c, False, pts, 2)
        # 箭头尖
        ap = (cx + r*math.cos(math.radians(60)), cy + r*math.sin(math.radians(60)))
        al = (ap[0]-4, ap[1]-3)
        ar = (ap[0]+4, ap[1]-3)
        pygame.draw.polygon(surface, c, [ap, al, ar])
    
    @staticmethod
    def _draw_moon(surface, x, y, s, c):
        """月亮图标"""
        cx, cy = x+s//2, y+s//2
        r = s//2 - 2
        pygame.draw.circle(surface, c, (cx, cy), r)
        # 阴影形成月牙
        sc = (25, 28, 40)  # 背景色
        pygame.draw.circle(surface, sc, (cx+r//2, cy-r//3), r-1)
    
    @staticmethod
    def _draw_sun(surface, x, y, s, c):
        """太阳图标"""
        cx, cy = x+s//2, y+s//2
        r = s//3
        pygame.draw.circle(surface, c, (cx, cy), r)
        # 光线
        for a in range(0, 360, 45):
            rad = math.radians(a)
            sx = cx + (r+2) * math.cos(rad)
            sy = cy + (r+2) * math.sin(rad)
            ex = cx + (s//2-1) * math.cos(rad)
            ey = cy + (s//2-1) * math.sin(rad)
            pygame.draw.line(surface, c, (sx, sy), (ex, ey), 2)
    
    @staticmethod
    def _draw_download(surface, x, y, s, c):
        """下载图标"""
        # 箭头向下
        pts = [(x+s//2, y+s-4), (x+4, y+s//2), (x+s-4, y+s//2)]
        pygame.draw.polygon(surface, c, pts)
        # 杆
        sw = max(2, s//8)
        pygame.draw.rect(surface, c, (x+s//2-sw//2, y+3, sw, s//2-2))
        # 底部横线
        pygame.draw.rect(surface, c, (x+2, y+s-4, s-4, 2))
    
    @staticmethod
    def _draw_desktop(surface, x, y, s, c):
        """桌面/显示器图标"""
        # 屏幕
        pygame.draw.rect(surface, c, (x+2, y+2, s-4, s*2//3-2), border_radius=2)
        dc = Icons._darken(c, 50)
        pygame.draw.rect(surface, dc, (x+5, y+5, s-10, s*2//3-10))
        # 底座
        pygame.draw.rect(surface, c, (x+s//4, y+s*2//3, s//2, s//3-2), border_radius=2)
    
    @staticmethod
    def _draw_image(surface, x, y, s, c):
        """图片图标"""
        # 外框
        pygame.draw.rect(surface, c, (x+2, y+2, s-4, s-4), border_radius=2)
        # 山和太阳
        lc = Icons._lighten(c, 50)
        pygame.draw.circle(surface, lc, (x+s*3//4, y+s//4), s//6)
        pts = [(x+4, y+s-6), (x+s//3, y+s//2), (x+s*2//3, y+s*2//3), (x+s-4, y+s-6)]
        pygame.draw.polygon(surface, lc, pts)
    
    @staticmethod
    def _draw_music(surface, x, y, s, c):
        """音乐图标"""
        nw = s//5
        # 音符杆
        pygame.draw.rect(surface, c, (x+s*2//3, y+3, nw, s-6))
        # 音符头
        pygame.draw.ellipse(surface, c, (x+3, y+s//2, s//2, s//3))
        # 旗标
        lc = Icons._lighten(c, 50)
        pts = [(x+s*2//3+nw, y+3), (x+s*2//3+nw+s//4, y+s//6), (x+s*2//3+nw, y+s//3)]
        pygame.draw.polygon(surface, lc, pts)
    
    @staticmethod
    def _draw_video(surface, x, y, s, c):
        """视频图标"""
        # 播放三角形
        lc = Icons._lighten(c, 40)
        pts = [(x+4, y+3), (x+s-4, y+s//2), (x+4, y+s-3)]
        pygame.draw.polygon(surface, lc, pts)
        # 外框
        pygame.draw.rect(surface, c, (x+1, y+1, s-2, s-2), 2, border_radius=2)
    
    @staticmethod
    def _draw_document(surface, x, y, s, c):
        """文档图标"""
        Icons._draw_file(surface, x, y, s, c)
        # 文档标记线
        lc = Icons._lighten(c, 60)
        pygame.draw.rect(surface, lc, (x+s//4, y+s//3, s//2, s//5), border_radius=1)
    
    @staticmethod
    def _draw_close(surface, x, y, s, c):
        """关闭X图标"""
        m = s//4
        pygame.draw.line(surface, c, (x+m, y+m), (x+s-m, y+s-m), 2)
        pygame.draw.line(surface, c, (x+s-m, y+m), (x+m, y+s-m), 2)
    
    @staticmethod
    def _draw_settings(surface, x, y, s, c):
        """齿轮设置图标"""
        cx, cy = x+s//2, y+s//2
        outer = s//2 - 2
        inner = s//4
        pygame.draw.circle(surface, c, (cx, cy), outer, 2)
        pygame.draw.circle(surface, c, (cx, cy), inner)
        # 齿
        for a in range(0, 360, 45):
            rad = math.radians(a)
            sx = cx + (outer-1) * math.cos(rad)
            sy = cy + (outer-1) * math.sin(rad)
            ex = cx + (outer+3) * math.cos(rad)
            ey = cy + (outer+3) * math.sin(rad)
            pygame.draw.line(surface, c, (sx, sy), (ex, ey), 2)
    
    @staticmethod
    def _draw_search(surface, x, y, s, c):
        """搜索图标"""
        cx, cy = x+s//3, y+s//3
        r = s//3
        pygame.draw.circle(surface, c, (cx, cy), r, 2)
        # 手柄
        sx = cx + r * math.cos(math.radians(45))
        sy = cy + r * math.sin(math.radians(45))
        ex, ey = x+s-3, y+s-3
        pygame.draw.line(surface, c, (sx, sy), (ex, ey), 2)
    
    @staticmethod
    def _draw_back(surface, x, y, s, c):
        """后退箭头"""
        pts = [(x+s-4, y+3), (x+4, y+s//2), (x+s-4, y+s-3)]
        pygame.draw.polygon(surface, c, pts)
    
    @staticmethod
    def _draw_forward(surface, x, y, s, c):
        """前进箭头"""
        pts = [(x+4, y+3), (x+s-4, y+s//2), (x+4, y+s-3)]
        pygame.draw.polygon(surface, c, pts)
    
    @staticmethod
    def _draw_plus(surface, x, y, s, c):
        """加号"""
        hw = s//2
        m = 2
        pygame.draw.rect(surface, c, (x+hw-m, y+3, m*2, s-6))
        pygame.draw.rect(surface, c, (x+3, y+hw-m, s-6, m*2))
    
    @staticmethod
    def _draw_default(surface, x, y, s, c):
        """默认圆点图标"""
        pygame.draw.circle(surface, c, (x+s//2, y+s//2), s//2-2)
    
    @staticmethod
    def _darken(color, amount):
        """变暗颜色"""
        return tuple(max(0, c - amount) for c in color[:3])
    
    @staticmethod
    def _lighten(color, amount):
        """变亮颜色"""
        return tuple(min(255, c + amount) for c in color[:3])


class IconMapper:
    """图标名称映射"""
    
    # 文件类型到图标的映射
    FILE_ICONS = {
        'folder': 'folder',
        'image': 'image',
        'audio': 'music', 
        'video': 'video',
        'archive': 'file',
        'code': 'file',
        'document': 'document',
        'default': 'file',
    }
    
    @staticmethod
    def get_file_icon(extension):
        """根据扩展名获取图标名称"""
        ext = extension.lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp']:
            return 'image'
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']:
            return 'audio'
        elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']:
            return 'video'
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz']:
            return 'archive'
        elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.json', '.xml']:
            return 'code'
        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md']:
            return 'document'
        else:
            return 'default'
    
    @staticmethod
    def get_icon_color(icon_type, colors):
        """获取图标颜色"""
        color_map = {
            'folder': colors['folder'],
            'image': colors.get('image', colors['file']),
            'audio': colors.get('audio', colors['file']),
            'video': colors.get('video', colors['file']),
            'archive': colors.get('archive', colors['file']),
            'code': colors.get('code', colors['file']),
            'document': colors.get('document', colors['file']),
            'default': colors['file'],
        }
        return color_map.get(icon_type, colors['file'])