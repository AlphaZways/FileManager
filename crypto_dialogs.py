"""
加密功能对话框模块
"""
import pygame
import os
import json
from crypto_manager import ECCKeyManager, ECCEncryptor, QRCodeManager
from io import BytesIO

class CryptoDialogManager:
    """加密对话框管理器"""
    
    def __init__(self, screen, config, fonts):
        self.screen = screen
        self.config = config
        self.fonts = fonts
        self.key_manager = ECCKeyManager()
        self.encryptor = ECCEncryptor(self.key_manager)
        
        # 对话框状态
        self.show_key_gen = False
        self.show_encrypt = False
        self.show_decrypt = False
        self.show_qr_display = False
        self.show_qr_scan = False
        
        # 当前显示的二维码
        self.current_qr_surface = None
        self.current_qr_type = None
        
        # 动画状态
        self.dialog_scale = 0.8
        self.overlay_alpha = 0
        
        # 输入状态
        self.input_text = ""
        self.input_active = False
        
        # 按钮区域
        self.buttons = []
        self.input_rect = None
    
    def reset_animation(self):
        """重置动画"""
        self.dialog_scale = 0.8
        self.overlay_alpha = 0
    
    def update_animation(self):
        """更新动画"""
        target_scale = 1.0
        target_alpha = 180
        
        self.dialog_scale += (target_scale - self.dialog_scale) * 0.15
        self.overlay_alpha += (target_alpha - self.overlay_alpha) * 0.15
        
        if abs(target_scale - self.dialog_scale) < 0.001:
            self.dialog_scale = target_scale
    
    def show_key_generation(self):
        """显示密钥生成对话框"""
        self.show_key_gen = True
        self.show_encrypt = False
        self.show_decrypt = False
        self.show_qr_display = False
        self.reset_animation()
        
        # 生成密钥对
        self.key_manager.generate_key_pair()
    
    def show_encrypt_dialog(self, file_path=None):
        """显示加密对话框"""
        self.show_key_gen = False
        self.show_encrypt = True
        self.show_decrypt = False
        self.show_qr_display = False
        self.reset_animation()
        self.encrypt_file_path = file_path
    
    def show_decrypt_dialog(self, file_path=None):
        """显示解密对话框"""
        self.show_key_gen = False
        self.show_encrypt = False
        self.show_decrypt = True
        self.show_qr_display = False
        self.reset_animation()
        self.decrypt_file_path = file_path
    
    def show_qr_code(self, qr_type='public'):
        """显示二维码"""
        self.show_qr_display = True
        self.reset_animation()
        
        key_data = self.key_manager.get_public_key_pem() if qr_type == 'public' else self.key_manager.get_private_key_pem()
        
        if key_data:
            qr_image = QRCodeManager.generate_key_qr(key_data, qr_type, box_size=6, border=3)
            qr_size = min(400, self.config.screen_height - 200)
            self.current_qr_surface = QRCodeManager.qr_to_pygame_surface(qr_image, qr_size)
            self.current_qr_type = qr_type
    
    def draw(self):
        """绘制对话框"""
        if not self.active:
            return
        
        self.update_animation()
        c = self.config.colors
        sw = self.config.screen_width
        sh = self.config.screen_height
        
        # 遮罩
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.overlay_alpha)))
        self.screen.blit(overlay, (0, 0))
        
        # 对话框
        width, height = 600, 500
        aw = int(width * self.dialog_scale)
        ah = int(height * self.dialog_scale)
        ax = (sw - aw) // 2
        ay = (sh - ah) // 2
        
        # 窗口
        dialog_rect = pygame.Rect(ax, ay, aw, ah)
        pygame.draw.rect(self.screen, c['bg'], dialog_rect, border_radius=12)
        pygame.draw.rect(self.screen, c['border'], dialog_rect, 2, border_radius=12)
        
        # 标题栏
        title_h = 45
        pygame.draw.rect(self.screen, c['sidebar'], 
                        (ax, ay, aw, title_h),
                        border_top_left_radius=12, border_top_right_radius=12)
        
        title_text = "文件加密" if self.mode == 'encrypt' else "文件解密"
        title_surf = self.fonts.render(title_text, 'large', c['text'])
        self.screen.blit(title_surf, (ax+20, ay+10))
        
        # 关闭按钮
        self.close_btn = pygame.Rect(ax+aw-40, ay+8, 32, 32)
        is_hover = self.close_btn.collidepoint(pygame.mouse.get_pos())
        close_color = (220, 80, 80) if is_hover else c['button']
        pygame.draw.rect(self.screen, close_color, self.close_btn, border_radius=6)
        close_surf = self.fonts.render("X", 'medium', (255,255,255))
        self.screen.blit(close_surf, (self.close_btn.x+8, self.close_btn.y+4))
        
        # 内容区域
        content_y = ay + title_h + 20
        
        # 显示二维码
        if self.showing_qr and self.qr_surface:
            qr_x = ax + (aw - self.qr_surface.get_width()) // 2
            qr_y = content_y
            
            qr_bg = pygame.Rect(qr_x-10, qr_y-10, 
                            self.qr_surface.get_width()+20, 
                            self.qr_surface.get_height()+20)
            pygame.draw.rect(self.screen, (255, 255, 255), qr_bg, border_radius=5)
            self.screen.blit(self.qr_surface, (qr_x, qr_y))
            
            content_y = qr_y + self.qr_surface.get_height() + 15
        
        # 状态文本
        for i, line in enumerate(self.status_text.split('\n')):
            color = c['text']
            # 成功消息用绿色
            if '完成' in line or '成功' in line:
                color = c.get('accent', (100, 200, 100))
            txt_surf = self.fonts.render(line, 'small', color)
            self.screen.blit(txt_surf, (ax+30, content_y + i*25))
            content_y += 25
        
        # 进度条
        if 0 < self.progress < 100:
            bar_y = content_y + 20
            bar_w = aw - 60
            bar_h = 6
            
            pygame.draw.rect(self.screen, c['input_bg'], 
                        (ax+30, bar_y, bar_w, bar_h), border_radius=3)
            
            fill_w = int(bar_w * self.progress / 100)
            if fill_w > 0:
                pygame.draw.rect(self.screen, c['accent'], 
                            (ax+30, bar_y, fill_w, bar_h), border_radius=3)
        
        # 按钮
        self.buttons = []
        btn_y = ay + ah - 55
        
        if self.mode == 'decrypt' and self.progress < 100:
            # 扫描二维码按钮
            scan_btn = pygame.Rect(ax+30, btn_y, 160, 35)
            is_hover = scan_btn.collidepoint(pygame.mouse.get_pos())
            bg = c['accent'] if not is_hover else tuple(min(255, v+20) for v in c['accent'][:3])
            pygame.draw.rect(self.screen, bg, scan_btn, border_radius=6)
            scan_txt = self.fonts.render("扫描二维码", 'small', (255,255,255))
            self.screen.blit(scan_txt, (scan_btn.x+15, scan_btn.y+8))
            self.buttons.append((scan_btn, self._scan_qr_decrypt))
            
            # 导入二维码按钮
            import_btn = pygame.Rect(ax+210, btn_y, 160, 35)
            is_hover = import_btn.collidepoint(pygame.mouse.get_pos())
            bg = c['button_hover'] if is_hover else c['button']
            pygame.draw.rect(self.screen, bg, import_btn, border_radius=6)
            import_txt = self.fonts.render("导入二维码", 'small', c['text'])
            self.screen.blit(import_txt, (import_btn.x+20, import_btn.y+8))
            self.buttons.append((import_btn, self._import_qr_decrypt))
        
        def _draw_dialog_background(self, width, height):
            """绘制对话框背景"""
            c = self.config.colors
            sw = self.config.screen_width
            sh = self.config.screen_height
            
            # 更新动画
            self.update_animation()
            
            # 遮罩
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.overlay_alpha)))
            self.screen.blit(overlay, (0, 0))
            
            # 对话框位置
            aw = int(width * self.dialog_scale)
            ah = int(height * self.dialog_scale)
            ax = (sw - aw) // 2
            ay = (sh - ah) // 2
            
            # 阴影
            shadow_rect = pygame.Rect(ax+5, ay+5, aw, ah)
            pygame.draw.rect(self.screen, (0, 0, 0, 40), shadow_rect, border_radius=12)
            
            # 主窗口
            dialog_rect = pygame.Rect(ax, ay, aw, ah)
            pygame.draw.rect(self.screen, c['bg'], dialog_rect, border_radius=12)
            pygame.draw.rect(self.screen, c['border'], dialog_rect, 2, border_radius=12)
            
            return ax, ay, aw, ah
    
    def _draw_title_bar(self, ax, ay, aw, title):
        """绘制标题栏"""
        c = self.config.colors
        title_h = 45
        
        pygame.draw.rect(self.screen, c['sidebar'], 
                        (ax, ay, aw, title_h),
                        border_top_left_radius=12, border_top_right_radius=12)
        
        title_surf = self.fonts.render(title, 'large', c['text'])
        self.screen.blit(title_surf, (ax+20, ay+10))
        
        # 关闭按钮
        close_rect = pygame.Rect(ax+aw-40, ay+8, 32, 32)
        is_hover = close_rect.collidepoint(pygame.mouse.get_pos())
        close_color = (220, 80, 80) if is_hover else c['button']
        pygame.draw.rect(self.screen, close_color, close_rect, border_radius=6)
        
        close_surf = self.fonts.render("X", 'medium', (255, 255, 255) if is_hover else c['text'])
        self.screen.blit(close_surf, (close_rect.x+8, close_rect.y+4))
        
        return close_rect, title_h
    
    def _draw_key_gen_dialog(self):
        """绘制密钥生成对话框"""
        width, height = 700, 500
        ax, ay, aw, ah = self._draw_dialog_background(width, height)
        close_rect, title_h = self._draw_title_bar(ax, ay, aw, "密钥生成")
        
        c = self.config.colors
        y = ay + title_h + 20
        
        # 密钥信息
        info_texts = [
            ("ECC密钥对已生成", 'large', c['text_bright']),
            ("算法: SECP256R1 (NIST P-256)", 'small', c['text_dim']),
            ("", 'small', c['text']),
            ("公钥 (可分享):", 'small', c['text_bright']),
        ]
        
        for text, font_name, color in info_texts:
            if text:
                surf = self.fonts.render(text, font_name, color)
                self.screen.blit(surf, (ax+30, y))
                y += 30
            else:
                y += 10
        
        # 公钥预览
        pub_key = self.key_manager.get_public_key_pem()
        if pub_key:
            lines = pub_key.split('\n')[:4]
            for line in lines:
                surf = self.fonts.render(line[:60], 'tiny', c['text_dim'])
                self.screen.blit(surf, (ax+40, y))
                y += 18
        
        y += 20
        
        # 按钮
        self.buttons = []
        btn_data = [
            ("显示公钥二维码", ax+30, y, 180, 35, lambda: self.show_qr_code('public')),
            ("显示私钥二维码", ax+230, y, 180, 35, lambda: self.show_qr_code('private')),
            ("保存密钥对", ax+30, y+45, 180, 35, self._save_key_pair),
            ("关闭", ax+230, y+45, 180, 35, self._close_all),
        ]
        
        for text, bx, by, bw, bh, action in btn_data:
            btn_rect = pygame.Rect(bx, by, bw, bh)
            is_hover = btn_rect.collidepoint(pygame.mouse.get_pos())
            bg = c['accent_hover'] if is_hover else c['accent']
            pygame.draw.rect(self.screen, bg, btn_rect, border_radius=6)
            
            txt_surf = self.fonts.render(text, 'small', (255, 255, 255))
            self.screen.blit(txt_surf, (bx+15, by+8))
            
            self.buttons.append((btn_rect, action))
        
        self._close_btn = close_rect
    
    def _draw_encrypt_dialog(self):
        """绘制加密对话框"""
        width, height = 600, 450
        ax, ay, aw, ah = self._draw_dialog_background(width, height)
        close_rect, title_h = self._draw_title_bar(ax, ay, aw, "文件加密")
        
        c = self.config.colors
        y = ay + title_h + 20
        
        # 文件信息
        if hasattr(self, 'encrypt_file_path') and self.encrypt_file_path:
            fname = os.path.basename(self.encrypt_file_path)
            surf = self.fonts.render(f"文件: {fname}", 'medium', c['text'])
            self.screen.blit(surf, (ax+30, y))
            y += 35
        
        # 公钥输入
        surf = self.fonts.render("请输入公钥 (或扫描二维码):", 'small', c['text_dim'])
        self.screen.blit(surf, (ax+30, y))
        y += 25
        
        # 输入框
        self.input_rect = pygame.Rect(ax+30, y, aw-60, 60)
        pygame.draw.rect(self.screen, c['input_bg'], self.input_rect, border_radius=5)
        pygame.draw.rect(self.screen, c['accent'] if self.input_active else c['border'], 
                        self.input_rect, 2, border_radius=5)
        
        # 显示输入的公钥（截断）
        display_text = self.input_text[:80] + "..." if len(self.input_text) > 80 else self.input_text
        if display_text:
            for i, line in enumerate(display_text.split('\n')[:3]):
                txt_surf = self.fonts.render(line, 'tiny', c['text'])
                self.screen.blit(txt_surf, (self.input_rect.x+10, self.input_rect.y+5+i*18))
        
        y += 75
        
        # 按钮
        self.buttons = []
        btn_data = [
            ("扫描二维码", ax+30, y, 150, 35, self._scan_qr_for_encrypt),
            ("使用已有公钥", ax+200, y, 150, 35, lambda: self.input_text == self.key_manager.get_public_key_pem() or ""),
            ("开始加密", ax+30, y+45, 150, 35, self._perform_encrypt),
            ("关闭", ax+200, y+45, 150, 35, self._close_all),
        ]
        
        for text, bx, by, bw, bh, action in btn_data:
            btn_rect = pygame.Rect(bx, by, bw, bh)
            is_hover = btn_rect.collidepoint(pygame.mouse.get_pos())
            bg = c['accent_hover'] if is_hover else c['accent']
            pygame.draw.rect(self.screen, bg, btn_rect, border_radius=6)
            
            txt_surf = self.fonts.render(text, 'small', (255, 255, 255))
            self.screen.blit(txt_surf, (bx+10, by+8))
            
            self.buttons.append((btn_rect, action))
        
        self._close_btn = close_rect
    
    def _draw_decrypt_dialog(self):
        """绘制解密对话框"""
        width, height = 600, 450
        ax, ay, aw, ah = self._draw_dialog_background(width, height)
        close_rect, title_h = self._draw_title_bar(ax, ay, aw, "文件解密")
        
        c = self.config.colors
        y = ay + title_h + 20
        
        # 文件信息
        if hasattr(self, 'decrypt_file_path') and self.decrypt_file_path:
            fname = os.path.basename(self.decrypt_file_path)
            surf = self.fonts.render(f"文件: {fname}", 'medium', c['text'])
            self.screen.blit(surf, (ax+30, y))
            y += 35
        
        # 私钥输入
        surf = self.fonts.render("请输入私钥 (或扫描二维码):", 'small', c['text_dim'])
        self.screen.blit(surf, (ax+30, y))
        y += 25
        
        # 输入框
        self.input_rect = pygame.Rect(ax+30, y, aw-60, 60)
        pygame.draw.rect(self.screen, c['input_bg'], self.input_rect, border_radius=5)
        pygame.draw.rect(self.screen, c['accent'] if self.input_active else c['border'], 
                        self.input_rect, 2, border_radius=5)
        
        display_text = self.input_text[:80] + "..." if len(self.input_text) > 80 else self.input_text
        if display_text:
            for i, line in enumerate(display_text.split('\n')[:3]):
                txt_surf = self.fonts.render(line, 'tiny', c['text'])
                self.screen.blit(txt_surf, (self.input_rect.x+10, self.input_rect.y+5+i*18))
        
        y += 75
        
        # 按钮
        self.buttons = []
        btn_data = [
            ("扫描二维码", ax+30, y, 150, 35, self._scan_qr_for_decrypt),
            ("使用已有私钥", ax+200, y, 150, 35, lambda: setattr(self, 'input_text', self.key_manager.get_private_key_pem() or "")),
            ("开始解密", ax+30, y+45, 150, 35, self._perform_decrypt),
            ("关闭", ax+200, y+45, 150, 35, self._close_all),
        ]
        
        for text, bx, by, bw, bh, action in btn_data:
            btn_rect = pygame.Rect(bx, by, bw, bh)
            is_hover = btn_rect.collidepoint(pygame.mouse.get_pos())
            bg = c['accent_hover'] if is_hover else c['accent']
            pygame.draw.rect(self.screen, bg, btn_rect, border_radius=6)
            
            txt_surf = self.fonts.render(text, 'small', (255, 255, 255))
            self.screen.blit(txt_surf, (bx+10, by+8))
            
            self.buttons.append((btn_rect, action))
        
        self._close_btn = close_rect
    
    def _draw_qr_display(self):
        """显示二维码"""
        if not self.current_qr_surface:
            return
        
        width, height = 550, 550
        ax, ay, aw, ah = self._draw_dialog_background(width, height)
        close_rect, title_h = self._draw_title_bar(ax, ay, aw, 
            f"{'公钥' if self.current_qr_type == 'public' else '私钥'}二维码")
        
        c = self.config.colors
        
        # 显示二维码
        qr_x = ax + (aw - self.current_qr_surface.get_width()) // 2
        qr_y = ay + title_h + 20
        
        # 白色背景
        qr_bg = pygame.Rect(qr_x-10, qr_y-10, 
                           self.current_qr_surface.get_width()+20, 
                           self.current_qr_surface.get_height()+20)
        pygame.draw.rect(self.screen, (255, 255, 255), qr_bg, border_radius=5)
        
        self.screen.blit(self.current_qr_surface, (qr_x, qr_y))
        
        # 提示文字
        y = qr_y + self.current_qr_surface.get_height() + 20
        tip = self.fonts.render("请使用手机扫描此二维码获取密钥", 'small', c['text_dim'])
        self.screen.blit(tip, (ax+30, y))
        
        # 保存按钮
        y += 35
        save_btn = pygame.Rect(ax+30, y, 150, 35)
        is_hover = save_btn.collidepoint(pygame.mouse.get_pos())
        bg = c['accent_hover'] if is_hover else c['accent']
        pygame.draw.rect(self.screen, bg, save_btn, border_radius=6)
        
        save_txt = self.fonts.render("保存二维码", 'small', (255, 255, 255))
        self.screen.blit(save_txt, (save_btn.x+20, save_btn.y+8))
        
        self.buttons = [(save_btn, self._save_qr_image)]
        self._close_btn = close_rect
    
    def _save_key_pair(self):
        """保存密钥对"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            key_data = self.key_manager.export_key_pair()
            with open(file_path, 'w') as f:
                json.dump(key_data, f, indent=2)
    
    def _save_qr_image(self):
        """保存二维码图片"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path and self.current_qr_surface:
            pygame.image.save(self.current_qr_surface, file_path)
    
    def _scan_qr_for_encrypt(self):
        """扫描二维码获取公钥"""
        result = QRCodeManager.decode_qr_from_camera()
        if result:
            if 'key' in result:
                self.input_text = result['key']
    
    def _scan_qr_for_decrypt(self):
        """扫描二维码获取私钥"""
        result = QRCodeManager.decode_qr_from_camera()
        if result:
            if 'key' in result:
                self.input_text = result['key']
    
    def _perform_encrypt(self):
        """执行加密"""
        if hasattr(self, 'encrypt_file_path') and self.input_text:
            try:
                output = self.encryptor.encrypt_file(
                    self.encrypt_file_path,
                    public_key_pem=self.input_text
                )
                print(f"文件已加密: {output}")
                self._close_all()
            except Exception as e:
                print(f"加密失败: {e}")
    
    def _perform_decrypt(self):
        """执行解密"""
        if hasattr(self, 'decrypt_file_path') and self.input_text:
            try:
                output = self.encryptor.decrypt_file(
                    self.decrypt_file_path,
                    private_key_pem=self.input_text
                )
                print(f"文件已解密: {output}")
                self._close_all()
            except Exception as e:
                print(f"解密失败: {e}")
    
    def _close_all(self):
        """关闭所有对话框"""
        self.show_key_gen = False
        self.show_encrypt = False
        self.show_decrypt = False
        self.show_qr_display = False
        self.buttons = []
    
    def handle_click(self, pos):
        """处理点击"""
        if hasattr(self, '_close_btn') and self._close_btn and self._close_btn.collidepoint(pos):
            self._close_all()
            return True
        
        for btn_rect, action in self.buttons:
            if btn_rect.collidepoint(pos):
                action()
                return True
        
        if self.input_rect and self.input_rect.collidepoint(pos):
            self.input_active = True
            return True
        else:
            self.input_active = False
        
        return False
    
    def handle_key(self, event):
        """处理键盘输入"""
        if self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.input_active = False
            elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # 粘贴
                try:
                    self.input_text = pygame.scrap.get(pygame.SCRAP_TEXT).decode('utf-8')
                except:
                    pass
            else:
                self.input_text += event.unicode
            return True
        return False
    
    def is_active(self):
        """是否有活动对话框"""
        return self.show_key_gen or self.show_encrypt or self.show_decrypt or self.show_qr_display