"""
文件编辑器模块
支持新建文件、重命名、编辑txt文件
"""
import pygame
import os
import math
from datetime import datetime

class FileCreator:
    """文件创建器"""
    
    @staticmethod
    def create_txt(path, filename="新建文档.txt"):
        """创建txt文件"""
        filepath = os.path.join(path, filename)
        filepath = FileCreator._get_unique_path(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("")
        return filepath
    
    @staticmethod
    def create_png(width=800, height=600, filename="新建图片.png"):
        """创建空白PNG图片"""
        from PIL import Image
        filepath = os.path.join(os.getcwd(), filename)
        filepath = FileCreator._get_unique_path(filepath)
        img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        img.save(filepath, 'PNG')
        return filepath
    
    @staticmethod
    def create_jpg(width=800, height=600, filename="新建图片.jpg"):
        """创建空白JPG图片"""
        from PIL import Image
        filepath = os.path.join(os.getcwd(), filename)
        filepath = FileCreator._get_unique_path(filepath)
        img = Image.new('RGB', (width, height), (255, 255, 255))
        img.save(filepath, 'JPEG', quality=95)
        return filepath
    
    @staticmethod
    def create_bmp(width=800, height=600, filename="新建图片.bmp"):
        """创建空白BMP图片"""
        from PIL import Image
        filepath = os.path.join(os.getcwd(), filename)
        filepath = FileCreator._get_unique_path(filepath)
        img = Image.new('RGB', (width, height), (255, 255, 255))
        img.save(filepath, 'BMP')
        return filepath
    
    @staticmethod
    def create_math_image(width=800, height=600, filename="数学图像.mth"):
        """创建数学图像文件"""
        from PIL import Image, ImageDraw
        filepath = os.path.join(os.getcwd(), filename)
        filepath = FileCreator._get_unique_path(filepath)
        
        img = Image.new('RGB', (width, height), (30, 30, 40))
        draw = ImageDraw.Draw(img)
        
        # 绘制坐标轴
        center_x, center_y = width // 2, height // 2
        draw.line([(50, center_y), (width - 50, center_y)], fill=(100, 100, 120), width=2)
        draw.line([(center_x, 50), (center_x, height - 50)], fill=(100, 100, 120), width=2)
        
        # 绘制网格
        for i in range(0, width, 50):
            draw.line([(i, 0), (i, height)], fill=(50, 50, 60), width=1)
        for i in range(0, height, 50):
            draw.line([(0, i), (width, i)], fill=(50, 50, 60), width=1)
        
        # 绘制正弦波
        points = []
        for x in range(50, width - 50):
            y = center_y - int(math.sin((x - center_x) / 50) * 100)
            points.append((x, y))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i+1]], fill=(0, 200, 100), width=2)
        
        img.save(filepath, 'PNG')
        return filepath
    
    @staticmethod
    def _get_unique_path(filepath):
        """获取唯一文件路径"""
        if not os.path.exists(filepath):
            return filepath
        
        base, ext = os.path.splitext(filepath)
        counter = 1
        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1


class FileRenamer:
    """文件重命名器"""
    
    @staticmethod
    def rename(old_path, new_name):
        """重命名文件"""
        if not os.path.exists(old_path):
            return False, "文件不存在"
        
        parent_dir = os.path.dirname(old_path)
        new_path = os.path.join(parent_dir, new_name)
        
        if os.path.exists(new_path):
            return False, "文件名已存在"
        
        try:
            os.rename(old_path, new_path)
            return True, new_path
        except Exception as e:
            return False, str(e)


class TxtEditor:
    """TXT文件编辑器"""
    
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.content = ""
        self.modified = False
        
        if file_path and os.path.exists(file_path):
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """加载文件"""
        self.file_path = file_path
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    self.content = f.read()
                return True
            except:
                continue
        
        self.content = ""
        return False
    
    def save(self):
        """保存文件"""
        if self.file_path:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            self.modified = False
            return True
        return False
    
    def save_as(self, file_path):
        """另存为"""
        self.file_path = file_path
        return self.save()
    
    def insert_text(self, text, position=None):
        """插入文本"""
        if position is None:
            position = len(self.content)
        self.content = self.content[:position] + text + self.content[position:]
        self.modified = True
    
    def delete_text(self, start, end):
        """删除文本"""
        self.content = self.content[:start] + self.content[end:]
        self.modified = True
    
    def replace_text(self, old, new):
        """替换文本"""
        self.content = self.content.replace(old, new)
        self.modified = True
    
    def get_lines(self):
        """获取行列表"""
        return self.content.split('\n')
    
    def get_content(self):
        """获取内容"""
        return self.content


class CreateFileDialog:
    """新建文件对话框"""
    
    def __init__(self, screen, config, fonts):
        self.screen = screen
        self.config = config
        self.fonts = fonts
        self.active = False
        self.current_path = ""
        
        # 动画
        self.scale = 0.8
        self.alpha = 0
        
        # 输入状态
        self.filename = ""
        self.selected_type = 0
        self.file_types = [
            (".txt", "文本文档", self._create_txt),
            (".png", "PNG图片", self._create_png),
            (".jpg", "JPG图片", self._create_jpg),
            (".bmp", "BMP图片", self._create_bmp),
            (".mth", "数学图像", self._create_math),
        ]
        
        self.result_message = ""
        self.close_btn = None
        self.buttons = []
    
    def show(self, current_path):
        self.active = True
        self.current_path = current_path
        self.filename = ""
        self.result_message = ""
        self.scale = 0.8
        self.alpha = 0
    
    def _create_txt(self):
        return FileCreator.create_txt(self.current_path, self.filename or "新建文档.txt")
    
    def _create_png(self):
        return FileCreator.create_png(filename=self.filename or "新建图片.png")
    
    def _create_jpg(self):
        return FileCreator.create_jpg(filename=self.filename or "新建图片.jpg")
    
    def _create_bmp(self):
        return FileCreator.create_bmp(filename=self.filename or "新建图片.bmp")
    
    def _create_math(self):
        return FileCreator.create_math_image(filename=self.filename or "数学图像.mth")
    
    def _do_create(self):
        """执行创建"""
        if self.selected_type < len(self.file_types):
            try:
                result = self.file_types[self.selected_type][2]()
                self.result_message = f"创建成功: {os.path.basename(result)}"
                return result
            except Exception as e:
                self.result_message = f"创建失败: {str(e)}"
        return None
    
    def update_animation(self):
        self.scale += (1.0 - self.scale) * 0.15
        self.alpha += (180 - self.alpha) * 0.15
    
    def draw(self):
        if not self.active:
            return
        
        self.update_animation()
        c = self.config.colors
        sw = self.config.screen_width
        sh = self.config.screen_height
        
        # 遮罩
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.alpha)))
        self.screen.blit(overlay, (0, 0))
        
        # 对话框
        width, height = 500, 400
        aw = int(width * self.scale)
        ah = int(height * self.scale)
        ax = (sw - aw) // 2
        ay = (sh - ah) // 2
        
        # 窗口
        rect = pygame.Rect(ax, ay, aw, ah)
        pygame.draw.rect(self.screen, c['bg'], rect, border_radius=12)
        pygame.draw.rect(self.screen, c['border'], rect, 2, border_radius=12)
        
        # 标题栏
        title_h = 40
        pygame.draw.rect(self.screen, c['sidebar'], 
                        (ax, ay, aw, title_h),
                        border_top_left_radius=12, border_top_right_radius=12)
        
        title = self.fonts.render("新建文件", 'large', c['text'])
        self.screen.blit(title, (ax+15, ay+8))
        
        # 关闭按钮
        self.close_btn = pygame.Rect(ax+aw-35, ay+5, 30, 30)
        is_hover = self.close_btn.collidepoint(pygame.mouse.get_pos())
        close_color = (220, 80, 80) if is_hover else c['button']
        pygame.draw.rect(self.screen, close_color, self.close_btn, border_radius=6)
        close_txt = self.fonts.render("X", 'medium', (255,255,255))
        self.screen.blit(close_txt, (self.close_btn.x+7, self.close_btn.y+3))
        
        y = ay + title_h + 15
        
        # 文件名输入
        lbl = self.fonts.render("文件名:", 'small', c['text_dim'])
        self.screen.blit(lbl, (ax+20, y))
        y += 25
        
        input_rect = pygame.Rect(ax+20, y, aw-40, 32)
        pygame.draw.rect(self.screen, c['input_bg'], input_rect, border_radius=5)
        pygame.draw.rect(self.screen, c['accent'], input_rect, 2, border_radius=5)
        
        name_surf = self.fonts.render(self.filename or "输入文件名...", 'small', 
                                     c['text'] if self.filename else c['text_dim'])
        self.screen.blit(name_surf, (input_rect.x+10, input_rect.y+6))
        
        self._input_rect = input_rect
        y += 45
        
        # 文件类型选择
        lbl = self.fonts.render("文件类型:", 'small', c['text_dim'])
        self.screen.blit(lbl, (ax+20, y))
        y += 25
        
        self.buttons = []
        for i, (ext, name, _) in enumerate(self.file_types):
            col = i % 2
            row = i // 2
            bx = ax + 20 + col * 230
            by = y + row * 38
            
            btn_rect = pygame.Rect(bx, by, 220, 34)
            is_hover = btn_rect.collidepoint(pygame.mouse.get_pos())
            is_selected = i == self.selected_type
            
            if is_selected:
                bg = c['accent']
                txt_color = (255, 255, 255)
            elif is_hover:
                bg = c['button_hover']
                txt_color = c['text']
            else:
                bg = c['button']
                txt_color = c['text']
            
            pygame.draw.rect(self.screen, bg, btn_rect, border_radius=5)
            
            type_txt = self.fonts.render(f"{ext} - {name}", 'small', txt_color)
            self.screen.blit(type_txt, (bx+10, by+7))
            
            self.buttons.append((btn_rect, lambda t=i: setattr(self, 'selected_type', t)))
        
        y += 85
        
        # 创建按钮
        create_btn = pygame.Rect(ax+aw//2-60, ay+ah-50, 120, 36)
        is_hover = create_btn.collidepoint(pygame.mouse.get_pos())
        bg = c['accent_hover'] if is_hover else c['accent']
        pygame.draw.rect(self.screen, bg, create_btn, border_radius=6)
        create_txt = self.fonts.render("创建", 'medium', (255,255,255))
        self.screen.blit(create_txt, (create_btn.x+35, create_btn.y+6))
        self.buttons.append((create_btn, self._do_create))
        
        # 结果消息
        if self.result_message:
            msg_color = (100, 255, 100) if "成功" in self.result_message else (255, 100, 100)
            msg_surf = self.fonts.render(self.result_message, 'small', msg_color)
            self.screen.blit(msg_surf, (ax+20, ay+ah-55))
    
    def handle_click(self, pos):
        if self.close_btn and self.close_btn.collidepoint(pos):
            self.active = False
            return True
        
        for btn_rect, action in self.buttons:
            if btn_rect.collidepoint(pos):
                action()
                return True
        
        if hasattr(self, '_input_rect') and self._input_rect.collidepoint(pos):
            return True
        
        return False
    
    def handle_key(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.filename = self.filename[:-1]
        elif event.key == pygame.K_RETURN:
            self._do_create()
        else:
            self.filename += event.unicode
        return True
    
    def is_active(self):
        return self.active


class RenameDialog:
    """重命名对话框"""
    
    def __init__(self, screen, config, fonts):
        self.screen = screen
        self.config = config
        self.fonts = fonts
        self.active = False
        self.file_path = ""
        self.new_name = ""
        self.result_message = ""
        
        self.scale = 0.8
        self.alpha = 0
        
        self.close_btn = None
        self.buttons = []
    
    def show(self, file_path):
        self.active = True
        self.file_path = file_path
        self.new_name = os.path.basename(file_path)
        self.result_message = ""
        self.scale = 0.8
        self.alpha = 0
    
    def _do_rename(self):
        success, result = FileRenamer.rename(self.file_path, self.new_name)
        if success:
            self.result_message = f"重命名成功: {os.path.basename(result)}"
        else:
            self.result_message = f"重命名失败: {result}"
        return success
    
    def update_animation(self):
        self.scale += (1.0 - self.scale) * 0.15
        self.alpha += (180 - self.alpha) * 0.15
    
    def draw(self):
        if not self.active:
            return
        
        self.update_animation()
        c = self.config.colors
        sw = self.config.screen_width
        sh = self.config.screen_height
        
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.alpha)))
        self.screen.blit(overlay, (0, 0))
        
        width, height = 450, 250
        aw = int(width * self.scale)
        ah = int(height * self.scale)
        ax = (sw - aw) // 2
        ay = (sh - ah) // 2
        
        rect = pygame.Rect(ax, ay, aw, ah)
        pygame.draw.rect(self.screen, c['bg'], rect, border_radius=12)
        pygame.draw.rect(self.screen, c['border'], rect, 2, border_radius=12)
        
        title_h = 40
        pygame.draw.rect(self.screen, c['sidebar'], 
                        (ax, ay, aw, title_h),
                        border_top_left_radius=12, border_top_right_radius=12)
        
        title = self.fonts.render("重命名", 'large', c['text'])
        self.screen.blit(title, (ax+15, ay+8))
        
        self.close_btn = pygame.Rect(ax+aw-35, ay+5, 30, 30)
        is_hover = self.close_btn.collidepoint(pygame.mouse.get_pos())
        close_color = (220, 80, 80) if is_hover else c['button']
        pygame.draw.rect(self.screen, close_color, self.close_btn, border_radius=6)
        close_txt = self.fonts.render("X", 'medium', (255,255,255))
        self.screen.blit(close_txt, (self.close_btn.x+7, self.close_btn.y+3))
        
        y = ay + title_h + 20
        
        lbl = self.fonts.render("新文件名:", 'small', c['text_dim'])
        self.screen.blit(lbl, (ax+20, y))
        y += 25
        
        input_rect = pygame.Rect(ax+20, y, aw-40, 32)
        pygame.draw.rect(self.screen, c['input_bg'], input_rect, border_radius=5)
        pygame.draw.rect(self.screen, c['accent'], input_rect, 2, border_radius=5)
        
        name_surf = self.fonts.render(self.new_name, 'small', c['text'])
        self.screen.blit(name_surf, (input_rect.x+10, input_rect.y+6))
        
        self._input_rect = input_rect
        
        y += 55
        
        self.buttons = []
        rename_btn = pygame.Rect(ax+aw//2-60, y, 120, 34)
        is_hover = rename_btn.collidepoint(pygame.mouse.get_pos())
        bg = c['accent_hover'] if is_hover else c['accent']
        pygame.draw.rect(self.screen, bg, rename_btn, border_radius=6)
        rename_txt = self.fonts.render("确认重命名", 'small', (255,255,255))
        self.screen.blit(rename_txt, (rename_btn.x+12, rename_btn.y+7))
        self.buttons.append((rename_btn, self._do_rename))
        
        if self.result_message:
            msg_color = (100, 255, 100) if "成功" in self.result_message else (255, 100, 100)
            msg_surf = self.fonts.render(self.result_message, 'small', msg_color)
            self.screen.blit(msg_surf, (ax+20, y-20))
    
    def handle_click(self, pos):
        if self.close_btn and self.close_btn.collidepoint(pos):
            self.active = False
            return True
        
        for btn_rect, action in self.buttons:
            if btn_rect.collidepoint(pos):
                action()
                return True
        
        return False
    
    def handle_key(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.new_name = self.new_name[:-1]
        elif event.key == pygame.K_RETURN:
            self._do_rename()
        else:
            self.new_name += event.unicode
        return True
    
    def is_active(self):
        return self.active


class TxtEditDialog:
    """TXT编辑对话框"""
    
    def __init__(self, screen, config, fonts):
        self.screen = screen
        self.config = config
        self.fonts = fonts
        self.active = False
        self.editor = None
        
        self.scale = 0.8
        self.alpha = 0
        
        self.close_btn = None
        self.buttons = []
        self.scroll_offset = 0
        self.cursor_pos = 0
        self.cursor_line = 0
        self.cursor_col = 0
    
    def show(self, file_path):
        self.active = True
        self.editor = TxtEditor(file_path)
        self.scale = 0.8
        self.alpha = 0
        self.scroll_offset = 0
    
    def update_animation(self):
        self.scale += (1.0 - self.scale) * 0.15
        self.alpha += (180 - self.alpha) * 0.15
    
    def draw(self):
        if not self.active or not self.editor:
            return
        
        self.update_animation()
        c = self.config.colors
        sw = self.config.screen_width
        sh = self.config.screen_height
        
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.alpha)))
        self.screen.blit(overlay, (0, 0))
        
        width, height = min(900, sw-60), min(600, sh-60)
        aw = int(width * self.scale)
        ah = int(height * self.scale)
        ax = (sw - aw) // 2
        ay = (sh - ah) // 2
        
        rect = pygame.Rect(ax, ay, aw, ah)
        pygame.draw.rect(self.screen, c['bg'], rect, border_radius=12)
        pygame.draw.rect(self.screen, c['border'], rect, 2, border_radius=12)
        
        title_h = 40
        pygame.draw.rect(self.screen, c['sidebar'], 
                        (ax, ay, aw, title_h),
                        border_top_left_radius=12, border_top_right_radius=12)
        
        fname = os.path.basename(self.editor.file_path) if self.editor.file_path else "未命名"
        title = self.fonts.render(f"编辑: {fname}", 'large', c['text'])
        self.screen.blit(title, (ax+15, ay+8))
        
        self.close_btn = pygame.Rect(ax+aw-35, ay+5, 30, 30)
        is_hover = self.close_btn.collidepoint(pygame.mouse.get_pos())
        close_color = (220, 80, 80) if is_hover else c['button']
        pygame.draw.rect(self.screen, close_color, self.close_btn, border_radius=6)
        close_txt = self.fonts.render("X", 'medium', (255,255,255))
        self.screen.blit(close_txt, (self.close_btn.x+7, self.close_btn.y+3))
        
        # 文本编辑区
        text_y = ay + title_h + 10
        text_rect = pygame.Rect(ax+15, text_y, aw-30, ah-title_h-70)
        pygame.draw.rect(self.screen, c['input_bg'], text_rect, border_radius=6)
        pygame.draw.rect(self.screen, c['border'], text_rect, 1, border_radius=6)
        
        old_clip = self.screen.get_clip()
        self.screen.set_clip(text_rect)
        
        lines = self.editor.get_lines()
        line_height = 20
        for i, line in enumerate(lines[:40]):
            ly = text_y + 8 + i * line_height - self.scroll_offset
            if ly > text_rect.bottom:
                break
            if ly < text_y:
                continue
            
            num = self.fonts.render(str(i+1).rjust(3), 'tiny', c['text_dim'])
            self.screen.blit(num, (text_rect.x+5, ly))
            
            txt = self.fonts.render(line[:100], 'small', c['text'])
            self.screen.blit(txt, (text_rect.x+35, ly))
        
        self.screen.set_clip(old_clip)
        
        # 保存按钮
        self.buttons = []
        btn_y = ay + ah - 45
        save_btn = pygame.Rect(ax+aw//2-60, btn_y, 120, 34)
        is_hover = save_btn.collidepoint(pygame.mouse.get_pos())
        bg = c['accent_hover'] if is_hover else c['accent']
        pygame.draw.rect(self.screen, bg, save_btn, border_radius=6)
        save_txt = self.fonts.render("保存", 'medium', (255,255,255))
        self.screen.blit(save_txt, (save_btn.x+35, save_btn.y+6))
        self.buttons.append((save_btn, self._do_save))
        
        if self.editor.modified:
            mod_txt = self.fonts.render("* 已修改", 'tiny', (255, 200, 50))
            self.screen.blit(mod_txt, (ax+15, btn_y+8))
    
    def _do_save(self):
        if self.editor:
            self.editor.save()
    
    def handle_click(self, pos):
        if self.close_btn and self.close_btn.collidepoint(pos):
            self.active = False
            return True
        
        for btn_rect, action in self.buttons:
            if btn_rect.collidepoint(pos):
                action()
                return True
        
        return False
    
    def handle_key(self, event):
        if self.editor:
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.editor.save()
                return True
        return False
    
    def handle_text_input(self, text):
        if self.editor:
            self.editor.insert_text(text)
            return True
        return False
    
    def is_active(self):
        return self.active