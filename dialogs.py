
"""对话框模块"""
import pygame
import os
import math
import time
from icons import Icons
from fonts import FontManager
from animations import ScaleAnimation, FadeAnimation, Easing

class Dialogs:
    def __init__(self, screen, config, fs):
        self.screen = screen
        self.config = config
        self.fs = fs
        self.fonts = FontManager()
        
        # 动画对象
        self.preview_anim = None
        self.settings_anim = None
        self.preview_scale = 0.8
        self.settings_scale = 0.8
        self.overlay_alpha = 0
        
        # 缓动函数
        self.easing = Easing.ease_out_back
        
        # 关闭按钮动画
        self.close_hover = 0
    
    def draw(self):
        if self.fs.preview_active:
            self._draw_preview()
        if self.fs.settings_active:
            self._draw_settings()
    
    def _init_preview_animation(self):
        """初始化预览动画"""
        self.preview_scale = 0.8
        self.overlay_alpha = 0
    
    def _init_settings_animation(self):
        """初始化设置动画"""
        self.settings_scale = 0.8
        self.overlay_alpha = 0
    
    def _draw_preview(self):
        config = self.config
        c = {
            'bg': config.get_transition_color('bg'),
            'sidebar': config.get_transition_color('sidebar'),
            'border': config.get_transition_color('border'),
            'text': config.get_transition_color('text'),
            'text_dim': config.get_transition_color('text_dim'),
            'input_bg': config.get_transition_color('input_bg'),
            'accent': config.get_transition_color('accent'),
            'accent_hover': config.get_transition_color('accent_hover'),
            'button': config.get_transition_color('button'),
            'button_hover': config.get_transition_color('button_hover'),
        }
        sw = self.config.screen_width
        sh = self.config.screen_height
        
        # 动画更新
        target_scale = 1.0
        target_alpha = 180
        
        self.preview_scale += (target_scale - self.preview_scale) * 0.15
        self.overlay_alpha += (target_alpha - self.overlay_alpha) * 0.15
        
        # 接近目标时直接设置
        if abs(target_scale - self.preview_scale) < 0.001:
            self.preview_scale = target_scale
        if abs(target_alpha - self.overlay_alpha) < 0.5:
            self.overlay_alpha = target_alpha
        
        # 遮罩
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.overlay_alpha)))
        self.screen.blit(overlay, (0, 0))
        
        # 窗口尺寸和位置
        pw = min(900, sw-100)
        ph = min(600, sh-100)
        px = (sw - pw) // 2
        py = (sh - ph) // 2
        
        # 缩放
        aw = int(pw * self.preview_scale)
        ah = int(ph * self.preview_scale)
        ax = px + (pw - aw) // 2
        ay = py + (ph - ah) // 2
        
        preview_rect = pygame.Rect(ax, ay, aw, ah)
        
        # 阴影效果
        if self.preview_scale > 0.85:
            shadow_alpha = int((self.preview_scale - 0.85) / 0.15 * 40)
            shadow_rect = pygame.Rect(ax+3, ay+3, aw, ah)
            pygame.draw.rect(self.screen, (0, 0, 0, shadow_alpha), shadow_rect, border_radius=10)
        
        # 主窗口
        pygame.draw.rect(self.screen, c['bg'], preview_rect, border_radius=10)
        pygame.draw.rect(self.screen, c['border'], preview_rect, 1, border_radius=10)
        
        # 标题栏
        title_h = 45
        pygame.draw.rect(self.screen, c['sidebar'], 
                        (ax, ay, aw, title_h), 
                        border_top_left_radius=10, border_top_right_radius=10)
        
        fname = os.path.basename(self.fs.preview_file_path) if self.fs.preview_file_path else ""
        title = self.fonts.render(f"预览: {fname}", 'large', c['text'])
        self.screen.blit(title, (ax+15, ay+8))
        
        # 关闭按钮 - 带悬停动画
        close_rect = pygame.Rect(ax+aw-38, ay+8, 30, 30)
        is_hover = close_rect.collidepoint(pygame.mouse.get_pos())
        
        target_hover = 1.0 if is_hover else 0.0
        self.close_hover += (target_hover - self.close_hover) * 0.2
        
        close_color = self._lerp_color(c['button'], (220, 80, 80), self.close_hover)
        pygame.draw.rect(self.screen, close_color, close_rect, border_radius=6)
        
        icon_color = (255, 255, 255) if self.close_hover > 0.5 else c['text']
        Icons.draw(self.screen, 'close', close_rect.x+5, close_rect.y+5, 20, icon_color)
        
        # 内容区域
        content_rect = pygame.Rect(ax+15, ay+title_h+10, aw-30, ah-title_h-60)
        pygame.draw.rect(self.screen, c['input_bg'], content_rect, border_radius=6)
        pygame.draw.rect(self.screen, c['border'], content_rect, 1, border_radius=6)
        
        # 文本内容
        old_clip = self.screen.get_clip()
        self.screen.set_clip(content_rect)
        
        lines = self.fs.preview_content.split('\n')
        for i, line in enumerate(lines[:30]):
            ly = content_rect.y + 8 + i*20
            if ly > content_rect.bottom - 15:
                break
            
            # 行号 - 淡入效果
            alpha = min(255, int((i + 1) * 30 * self.preview_scale))
            num = self.fonts.render(str(i+1).rjust(3), 'tiny', (*c['text_dim'][:3], alpha))
            self.screen.blit(num, (content_rect.x+5, ly))
            
            txt = self.fonts.render(line[:90], 'small', c['text'])
            txt.set_alpha(alpha)
            self.screen.blit(txt, (content_rect.x+35, ly))
        
        self.screen.set_clip(old_clip)
        
        # 底部按钮
        btny = ay + ah - 45
        btnw, btnh = 100, 32
        
        # 打开按钮
        open_btn = pygame.Rect(ax+aw//2-btnw-10, btny, btnw, btnh)
        open_hover = open_btn.collidepoint(pygame.mouse.get_pos())
        open_color = c['accent_hover'] if open_hover else c['accent']
        
        pygame.draw.rect(self.screen, open_color, open_btn, border_radius=6)
        otxt = self.fonts.render("打开文件", 'small', (255,255,255))
        self.screen.blit(otxt, (open_btn.x+15, open_btn.y+5))
        
        # 设置按钮
        set_btn = pygame.Rect(ax+aw//2+10, btny, btnw, btnh)
        set_hover = set_btn.collidepoint(pygame.mouse.get_pos())
        set_color = c['button_hover'] if set_hover else c['button']
        
        pygame.draw.rect(self.screen, set_color, set_btn, border_radius=6)
        stxt = self.fonts.render("设置", 'small', c['text'])
        self.screen.blit(stxt, (set_btn.x+30, set_btn.y+5))
        
        self._preview_close = close_rect
        self._preview_open = open_btn
        self._preview_set = set_btn
    
    def _draw_settings(self):
        c = self.config.colors
        sw = self.config.screen_width
        sh = self.config.screen_height
        
        # 动画
        target_scale = 1.0
        target_alpha = 180
        
        self.settings_scale += (target_scale - self.settings_scale) * 0.15
        self.overlay_alpha += (target_alpha - self.overlay_alpha) * 0.15
        
        if abs(target_scale - self.settings_scale) < 0.001:
            self.settings_scale = target_scale
        
        # 遮罩
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.overlay_alpha)))
        self.screen.blit(overlay, (0, 0))
        
        pw, ph = 500, 380
        px = (sw - pw) // 2
        py = (sh - ph) // 2
        
        aw = int(pw * self.settings_scale)
        ah = int(ph * self.settings_scale)
        ax = px + (pw - aw) // 2
        ay = py + (ph - ah) // 2
        
        rect = pygame.Rect(ax, ay, aw, ah)
        
        # 窗口
        pygame.draw.rect(self.screen, c['bg'], rect, border_radius=10)
        pygame.draw.rect(self.screen, c['border'], rect, 1, border_radius=10)
        
        # 标题
        title_h = 45
        pygame.draw.rect(self.screen, c['sidebar'], 
                        (ax, ay, aw, title_h), 
                        border_top_left_radius=10, border_top_right_radius=10)
        
        title = self.fonts.render("设置文件打开方式", 'large', c['text'])
        self.screen.blit(title, (ax+15, ay+8))
        
        # 关闭按钮
        close_rect = pygame.Rect(ax+aw-38, ay+8, 30, 30)
        is_hover = close_rect.collidepoint(pygame.mouse.get_pos())
        close_color = c['button_hover'] if is_hover else c['button']
        pygame.draw.rect(self.screen, close_color, close_rect, border_radius=6)
        Icons.draw(self.screen, 'close', close_rect.x+5, close_rect.y+5, 20, c['text'])
        
        # 信息
        if self.fs.settings_file:
            fname = os.path.basename(self.fs.settings_file)
            ext = os.path.splitext(fname)[1]
            
            y = ay + 60
            for txt, clr in [
                (f"文件: {fname}", c['text']),
                (f"扩展名: {ext}", c['text_dim']),
            ]:
                s = self.fonts.render(txt, 'medium', clr)
                self.screen.blit(s, (ax+20, y))
                y += 30
            
            y += 10
            pygame.draw.line(self.screen, c['border'], (ax+15, y), (ax+aw-15, y))
            
            y += 15
            s = self.fonts.render("选择程序:", 'small', c['text_dim'])
            self.screen.blit(s, (ax+20, y))
            
            y += 30
            programs = ['default', 'notepad', 'gedit', 'code', 'vim', 'nano']
            
            self._settings_btns = []
            for i, prog in enumerate(programs):
                bx = ax + 20 + (i%3)*155
                by = y + (i//3)*40
                
                btn = pygame.Rect(bx, by, 140, 32)
                is_sel = self.fs.associations.get(ext) == prog
                is_hover = btn.collidepoint(pygame.mouse.get_pos())
                
                if is_sel:
                    bg = c['accent']
                elif is_hover:
                    bg = c['button_hover']
                else:
                    bg = c['button']
                
                pygame.draw.rect(self.screen, bg, btn, border_radius=5)
                
                tc = (255,255,255) if is_sel else c['text']
                ts = self.fonts.render(prog, 'small', tc)
                self.screen.blit(ts, (btn.x+15, btn.y+5))
                
                self._settings_btns.append((btn, prog))
        
        self._settings_close = close_rect
    
    def reset_animations(self):
        """重置动画状态"""
        self.preview_scale = 0.8
        self.settings_scale = 0.8
        self.overlay_alpha = 0
        self.close_hover = 0
    
    def _lerp_color(self, color1, color2, t):
        """颜色插值"""
        if t <= 0:
            return color1
        if t >= 1:
            return color2
        
        result = []
        for i in range(min(len(color1), len(color2))):
            result.append(int(color1[i] + (color2[i] - color1[i]) * t))
        return tuple(result)