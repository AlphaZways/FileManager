"""UI渲染模块"""
import pygame
import math
import time
from icons import Icons, IconMapper
from fonts import FontManager
from file_ops import FileOperations

class UIRenderer:
    def __init__(self, screen, config, fs):
        self.screen = screen
        self.config = config
        self.fs = fs
        self.fonts = FontManager()
        
        self.scroll_smooth = 0
        
        self.hover_states = {}
        self.hover_times = {}
        
        self.theme_btn = None
        self.nav_btns = []
        self.quick_items = []
        self.path_rect = None
        
        self.file_animations = {}
        
        self.last_frame_time = time.time()
        self.delta_time = 0.016
    
    def draw_all(self):
        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        self.screen.fill(self.config.colors['bg'])
        self._draw_sidebar()
        self._draw_main_area()
    
    def _animate_hover(self, element_id, is_hover):
        if element_id not in self.hover_states:
            self.hover_states[element_id] = 0.0
        
        target = 1.0 if is_hover else 0.0
        
        if self.hover_states[element_id] != target:
            self.hover_states[element_id] += (target - self.hover_states[element_id]) * 0.2
            
            if abs(self.hover_states[element_id] - target) < 0.01:
                self.hover_states[element_id] = target
        
        return self.hover_states[element_id]
    
    def _draw_sidebar(self):
        c = self.config.colors
        sw = self.config.sidebar_width
        sh = self.config.screen_height
        
        # 背景
        pygame.draw.rect(self.screen, c['sidebar'], (0, 0, sw, sh))
        pygame.draw.line(self.screen, c['border'], (sw-1, 0), (sw-1, sh))
        
        # 标题
        title = self.fonts.render("文件管理", 'title', c['text_bright'])
        self.screen.blit(title, (15, 15))
        
        ver = self.fonts.render("v2.0", 'tiny', c['text_dim'])
        self.screen.blit(ver, (15, 48))
        
        # 主题按钮
        self.theme_btn = pygame.Rect(sw - 40, 15, 30, 30)
        is_hover = self.theme_btn.collidepoint(pygame.mouse.get_pos())
        bg = c['button_hover'] if is_hover else c['button']
        self._round_rect(self.theme_btn, bg, 6)
        
        icon = 'sun' if self.config.current_theme == 'dark' else 'moon'
        Icons.draw(self.screen, icon, self.theme_btn.x+5, self.theme_btn.y+5, 20, c['text'])
        
        # 导航按钮
        y = 70
        buttons = [
            ('home', '主目录'),
            ('up', '上级'),
            ('refresh', '刷新'),
        ]
        
        self.nav_btns = []
        for icon_name, label in buttons:
            rect = pygame.Rect(10, y, sw-20, 34)
            is_hover = rect.collidepoint(pygame.mouse.get_pos())
            bg = c['button_hover'] if is_hover else c['button']
            self._round_rect(rect, bg, 5)
            
            Icons.draw(self.screen, icon_name, rect.x+8, rect.y+7, 20, c['text'])
            
            lbl = self.fonts.render(label, 'small', c['text'])
            self.screen.blit(lbl, (rect.x+38, rect.y+7))
            
            self.nav_btns.append(rect)
            y += 40
        
        # 分隔线
        y += 5
        pygame.draw.line(self.screen, c['border'], (15, y), (sw-15, y))
        
        # 快速访问
        y += 15
        qtitle = self.fonts.render("快速访问", 'tiny', c['text_dim'])
        self.screen.blit(qtitle, (15, y))
        
        y += 22
        quick_icons = {
            "文档": 'document', "下载": 'download', "桌面": 'desktop',
            "图片": 'image', "音乐": 'music', "视频": 'video',
        }
        
        self.quick_items = []
        for name, path in self.fs.get_quick_paths():
            rect = pygame.Rect(10, y, sw-20, 28)
            is_hover = rect.collidepoint(pygame.mouse.get_pos())
            
            if is_hover:
                self._round_rect(rect, c['hover'], 4)
            
            icon_name = quick_icons.get(name, 'folder')
            icon_color = c['text'] if is_hover else c['text_dim']
            Icons.draw(self.screen, icon_name, rect.x+8, rect.y+5, 18, icon_color)
            
            lbl = self.fonts.render(name, 'small', icon_color)
            self.screen.blit(lbl, (rect.x+34, rect.y+4))
            
            self.quick_items.append((rect, path))
            y += 32
    
    def _draw_main_area(self):
        c = self.config.colors
        mx = self.config.sidebar_width
        mw = self.config.screen_width - mx
        
        # 路径栏
        self.path_rect = pygame.Rect(mx+10, 10, mw-20, 40)
        self._round_rect(self.path_rect, c['input_bg'], 8)
        
        Icons.draw(self.screen, 'folder', self.path_rect.x+10, self.path_rect.y+10, 20, c['folder'])
        
        path_text = self.fs.current_path
        max_chars = (mw - 80) // 12
        if len(path_text) > max_chars:
            path_text = "..." + path_text[-(max_chars-3):]
        
        path_surf = self.fonts.render(path_text, 'small', c['text'])
        if path_surf.get_width() > mw - 80:
            path_surf = self.fonts.render(path_text, 'tiny', c['text'])
        
        self.screen.blit(path_surf, (self.path_rect.x + 40, self.path_rect.y + 10))
        
        # 文件列表头
        header_y = 60
        headers = [
            ("名称", mx + 45),
            ("大小", mx + 400),
            ("修改时间", mx + 530),
            ("类型", mx + 680),
        ]
        
        hdr_rect = pygame.Rect(mx+10, header_y-2, mw-20, 26)
        self._round_rect(hdr_rect, c['hover'], 4)
        
        for label, x_pos in headers:
            surf = self.fonts.render(label, 'tiny', c['text_dim'])
            self.screen.blit(surf, (x_pos, header_y+2))
        
        pygame.draw.line(self.screen, c['border'], (mx+10, header_y+28), (mx+mw-10, header_y+28))
        
        # 文件列表
        list_y = header_y + 35
        visible_h = self.config.screen_height - list_y - 20
        
        self.fs.scroll_offset += (self.fs.target_scroll - self.fs.scroll_offset) * 0.2
        
        for i, fi in enumerate(self.fs.files):
            y = list_y + i * self.config.item_height - self.fs.scroll_offset
            
            if y + self.config.item_height < list_y - 5:
                continue
            if y > self.config.screen_height + 5:
                break
            
            self._draw_file_row(fi, i, y, mx, mw)
        
        # 滚动条
        if self.fs.max_scroll > 0:
            sx = mx + mw - 14
            sy = list_y
            sh = visible_h
            sw = 8
            
            pygame.draw.rect(self.screen, c['scrollbar'], (sx, sy, sw, sh), border_radius=4)
            
            thumb_h = max(30, (visible_h / (visible_h + self.fs.max_scroll)) * sh)
            thumb_y = sy + (self.fs.scroll_offset / self.fs.max_scroll) * (sh - thumb_h)
            
            is_hover = pygame.Rect(sx, thumb_y, sw, thumb_h).collidepoint(pygame.mouse.get_pos())
            thumb_progress = self._animate_hover('scrollbar', is_hover)
            
            thumb_color = self._lerp_color(c['scrollbar_thumb'], 
                                          self._lighten_color(c['scrollbar_thumb'], 30), 
                                          thumb_progress)
            thumb_width = sw + thumb_progress * 2
            
            pygame.draw.rect(self.screen, thumb_color, 
                           (sx - thumb_progress, thumb_y, thumb_width, thumb_h), 
                           border_radius=4)
    
    def _draw_file_row(self, fi, index, y, mx, mw):
        c = self.config.colors
        rect = pygame.Rect(mx+10, y, mw-25, self.config.item_height)
        
        is_selected = self.fs.selected_file == fi['path']
        is_hover = rect.collidepoint(pygame.mouse.get_pos())
        
        anim_id = f'file_{index}'
        hover_progress = self._animate_hover(anim_id, is_hover)
        select_progress = self._animate_hover(f'select_{index}', is_selected)
        
        if is_selected:
            bg_color = self._lerp_color(c['hover'], c['selected'], select_progress)
            self._round_rect(rect, bg_color, 5)
            border_alpha = int(select_progress * 255)
            border_color = (*c['accent'][:3], border_alpha)
            pygame.draw.rect(self.screen, border_color, rect, 1, border_radius=5)
        elif is_hover or hover_progress > 0.01:
            bg_alpha = int(hover_progress * 255)
            bg_color = (*c['hover'][:3], bg_alpha)
            self._round_rect(rect, bg_color, 5)
        
        x_offset = hover_progress * 5
        y_offset = hover_progress * -1
        
        icon_scale = 1.0 + hover_progress * 0.15
        icon_size = int(20 * icon_scale)
        
        if fi['is_dir']:
            icon_name = 'folder'
            icon_color = c['folder']
        else:
            icon_name = IconMapper.get_file_icon(fi['extension'])
            icon_color = IconMapper.get_icon_color(icon_name, c)
        
        if hover_progress > 0:
            icon_color = self._lighten_color(icon_color, int(hover_progress * 40))
        
        Icons.draw(self.screen, icon_name, 
                  rect.x + 8 + x_offset, 
                  y + 8 + y_offset, 
                  icon_size, icon_color)
        
        name = fi['name']
        if len(name) > self.config.max_filename_length:
            name = name[:self.config.max_filename_length-3] + "..."
        
        text_color = self._lerp_color(c['text'], c['text_bright'], hover_progress)
        name_surf = self.fonts.render(name, 'medium', text_color)
        self.screen.blit(name_surf, (rect.x + 38 + x_offset, y + 6 + y_offset))
        
        if not fi['is_dir']:
            size_text = FileOperations.format_size(fi['size'])
            size_surf = self.fonts.render(size_text, 'small', c['text_dim'])
            self.screen.blit(size_surf, (mx + 400, y + 8 + y_offset))
            
            date_text = FileOperations.format_date(fi['modified'])
            date_surf = self.fonts.render(date_text, 'small', c['text_dim'])
            self.screen.blit(date_surf, (mx + 530, y + 8 + y_offset))
            
            ext = fi['extension'] or "文件"
            type_surf = self.fonts.render(ext, 'small', c['text_dim'])
            self.screen.blit(type_surf, (mx + 680, y + 8 + y_offset))
    
    def draw_context_menu(self, event_handler):
        """绘制右键菜单"""
        if not event_handler.context_menu_active:
            return
        
        c = self.config.colors
        pos = event_handler.context_menu_pos
        file_info = event_handler.context_menu_file
        
        if file_info is None:
            return
        
        menu_items = []
        
        # ===== 根据文件类型构建菜单 =====
        if file_info['is_dir']:
            # 文件夹菜单
            menu_items = [
                (" 打开", lambda: self.fs.navigate(file_info['path'])),
                ("", None),
                (" 新建文件", lambda: event_handler._menu_new_file(file_info)),
            ]
        else:
            # 文件菜单
            if file_info['name'].endswith('.de'):
                # .de 加密文件 - 显示解密
                menu_items = [
                    (" 解密", lambda: event_handler._menu_decrypt(file_info)),
                    ("", None),  # 分隔线
                    (" 预览", lambda: self.fs.open_selected()),
                ]
            else:
                # 普通文件 - 显示加密
                menu_items = [
                    (" 加密", lambda: event_handler._menu_encrypt(file_info)),
                    (" 打开", lambda: self.fs.open_selected()),
                ]
                
    
        # 通用菜单项
        menu_items.extend([
            ("", None),  # 分隔线
            (" 更改打开方式", lambda: event_handler._menu_open_with(file_info)),
            (" 复制路径", lambda: event_handler._menu_copy_path(file_info)),
            (" 属性", lambda: event_handler._menu_properties(file_info)),
            ("", None),  # 分隔线
            (" 删除", lambda: event_handler._menu_delete(file_info)),
            ("✏ 编辑", lambda: event_handler._menu_edit_file(file_info)) if file_info['name'].endswith('.txt') else ("", None),
            ("✏ 重命名", lambda: event_handler._menu_rename_file(file_info)),
        ])
        
        # 计算菜单尺寸
        menu_width = 200
        item_height = 30
        sep_height = 6
        
        total_height = sum(sep_height if text == "" else item_height for text, _ in menu_items)
        
        # 菜单位置
        mx, my = pos
        
        # 确保菜单不超出屏幕
        if mx + menu_width > self.config.screen_width:
            mx = self.config.screen_width - menu_width - 10
        if my + total_height > self.config.screen_height:
            my = self.config.screen_height - total_height - 10
        if mx < 5:
            mx = 5
        if my < 5:
            my = 5
        
        # 绘制阴影
        shadow_rect = pygame.Rect(mx+3, my+3, menu_width, total_height + 8)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # 绘制菜单背景
        menu_rect = pygame.Rect(mx, my, menu_width, total_height + 8)
        pygame.draw.rect(self.screen, c['bg'], menu_rect, border_radius=8)
        pygame.draw.rect(self.screen, c['border'], menu_rect, 2, border_radius=8)
        
        # 绘制菜单项
        y = my + 4
        event_handler.context_menu_rects = []
        
        for text, action in menu_items:
            if text == "":
                # 分隔线
                line_y = y + sep_height // 2
                pygame.draw.line(self.screen, c['border'], 
                            (mx + 15, line_y), 
                            (mx + menu_width - 15, line_y), 1)
                y += sep_height
            else:
                item_rect = pygame.Rect(mx + 4, y, menu_width - 8, item_height)
                is_hover = item_rect.collidepoint(pygame.mouse.get_pos())
                
                # 悬停高亮
                if is_hover:
                    pygame.draw.rect(self.screen, c['hover'], item_rect, border_radius=4)
                
                # 颜色设置
                if '删除' in text:
                    text_color = (255, 80, 80)
                elif '加密' in text:
                    text_color = c['accent']  # 蓝色/绿色高亮
                elif '解密' in text:
                    text_color = (255, 200, 50)  # 金色高亮
                else:
                    text_color = c['text']
                
                # 渲染文本
                txt_surf = self.fonts.render(text, 'small', text_color)
                self.screen.blit(txt_surf, (mx + 15, y + 5))
                
                # 保存菜单项
                if action:
                    event_handler.context_menu_rects.append((item_rect, action))
                
                y += item_height
    def _lerp_color(self, color1, color2, t):
        if t <= 0:
            return color1
        if t >= 1:
            return color2
        result = []
        for i in range(min(len(color1), len(color2))):
            result.append(int(color1[i] + (color2[i] - color1[i]) * t))
        return tuple(result)
    
    def _lighten_color(self, color, amount):
        return tuple(min(255, c + amount) for c in color[:3])
    
    @staticmethod
    def _round_rect(rect, color, radius):
        surface = pygame.display.get_surface()
        if surface:
            if len(color) == 4:
                temp_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(temp_surf, color, temp_surf.get_rect(), border_radius=radius)
                surface.blit(temp_surf, rect.topleft)
            else:
                pygame.draw.rect(surface, color, rect, border_radius=radius)