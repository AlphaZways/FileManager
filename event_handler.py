"""事件处理模块"""
import pygame
import os
from file_ops import FileOperations

class EventHandler:
    def __init__(self, app):
        self.app = app
        
        self.context_menu_active = False
        self.context_menu_pos = (0, 0)
        self.context_menu_file = None
        self.context_menu_rects = []
        self.context_menu_is_blank = False  # 是否是空白处右键
    
    def handle(self):
        """处理所有事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                self._resize(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # ===== 对话框优先处理（防止穿透） =====
                
                # 1. 文本编辑对话框（最高优先级）
                if hasattr(self.app, 'txt_edit_dialog') and self.app.txt_edit_dialog.is_active():
                    if event.button == 1:
                        self.app.txt_edit_dialog.handle_click(event.pos)
                    elif event.button == 4:
                        self.app.txt_edit_dialog.scroll_offset = max(0, self.app.txt_edit_dialog.scroll_offset - 30)
                    elif event.button == 5:
                        self.app.txt_edit_dialog.scroll_offset += 30
                    continue  # ✅ 吞掉事件，不往下传递
                
                # 2. 创建文件对话框
                if hasattr(self.app, 'create_dialog') and self.app.create_dialog.is_active():
                    if event.button == 1:
                        self.app.create_dialog.handle_click(event.pos)
                    continue  # ✅ 吞掉事件
                
                # 3. 重命名对话框
                if hasattr(self.app, 'rename_dialog') and self.app.rename_dialog.is_active():
                    if event.button == 1:
                        self.app.rename_dialog.handle_click(event.pos)
                    continue  # ✅ 吞掉事件
                
                # 4. 加密对话框
                if hasattr(self.app, 'crypto_dialog') and self.app.crypto_dialog is not None:
                    if self.app.crypto_dialog.is_active():
                        if event.button == 1:
                            self.app.crypto_dialog.handle_click(event.pos)
                        continue  # ✅ 吞掉事件
                
                # 5. 预览对话框
                if self.app.fs.preview_active:
                    if event.button == 1:
                        self._check_preview_dialog_click(event.pos)
                    continue  # ✅ 吞掉事件
                
                # 6. 设置对话框
                if self.app.fs.settings_active:
                    if event.button == 1:
                        self._check_settings_dialog_click(event.pos)
                    continue  # ✅ 吞掉事件
                
                # ===== 没有对话框打开，正常处理 =====
                
                if event.button == 1:
                    if self.context_menu_active:
                        if self._check_context_menu_click(event.pos):
                            continue
                        else:
                            self.context_menu_active = False
                            self.context_menu_rects = []
                            self.context_menu_is_blank = False
                            continue
                    
                    self._handle_left_click(event.pos)
                
                elif event.button == 3:
                    if self.context_menu_active:
                        self.context_menu_active = False
                        self.context_menu_rects = []
                        self.context_menu_is_blank = False
                    
                    self._handle_right_click(event.pos)
                
                elif event.button == 4:
                    self._scroll(-60)
                elif event.button == 5:
                    self._scroll(60)
            
            elif event.type == pygame.KEYDOWN:
                # 对话框键盘事件优先
                if hasattr(self.app, 'txt_edit_dialog') and self.app.txt_edit_dialog.is_active():
                    self.app.txt_edit_dialog.handle_key(event)
                    continue
                
                if hasattr(self.app, 'create_dialog') and self.app.create_dialog.is_active():
                    self.app.create_dialog.handle_key(event)
                    continue
                
                if hasattr(self.app, 'rename_dialog') and self.app.rename_dialog.is_active():
                    self.app.rename_dialog.handle_key(event)
                    continue
                
                if self.context_menu_active:
                    if event.key == pygame.K_ESCAPE:
                        self.context_menu_active = False
                        self.context_menu_rects = []
                        self.context_menu_is_blank = False
                        continue
                
                self._handle_key(event)
            
            elif event.type == pygame.TEXTINPUT:
                # 文本输入只给编辑对话框
                if hasattr(self.app, 'txt_edit_dialog') and self.app.txt_edit_dialog.is_active():
                    self.app.txt_edit_dialog.handle_text_input(event.text)
    def _check_context_menu_click(self, pos):
        """检查是否点击了右键菜单项"""
        for item in self.context_menu_rects:
            rect = item[0]      # 矩形
            action = item[1]    # 回调函数
            if rect.collidepoint(pos):
                action()
                self.context_menu_active = False
                self.context_menu_rects = []
                self.context_menu_is_blank = False
                return True
            return False
        def _check_create_dialog_click(self, pos):
            if hasattr(self.app, 'create_dialog') and self.app.create_dialog.is_active():
                return self.app.create_dialog.handle_click(pos)
            return False
        
        def _check_rename_dialog_click(self, pos):
            if hasattr(self.app, 'rename_dialog') and self.app.rename_dialog.is_active():
                return self.app.rename_dialog.handle_click(pos)
            return False
        
        def _check_txt_edit_dialog_click(self, pos):
            if hasattr(self.app, 'txt_edit_dialog') and self.app.txt_edit_dialog.is_active():
                return self.app.txt_edit_dialog.handle_click(pos)
            return False
        
        def _check_context_menu_click(self, pos):
            for item in self.context_menu_rects:
                rect = item[0]
                action = item[1]
                if rect.collidepoint(pos):
                    action()
                    self.context_menu_active = False
                    self.context_menu_rects = []
                    self.context_menu_is_blank = False
                    return True
            return False
    
    def _check_crypto_dialog_click(self, pos):
        if not hasattr(self.app, 'crypto_dialog') or self.app.crypto_dialog is None:
            return False
        crypto = self.app.crypto_dialog
        if hasattr(crypto, 'is_active') and crypto.is_active():
            if hasattr(crypto, 'handle_click'):
                return crypto.handle_click(pos)
        return False
    
    def _check_preview_dialog_click(self, pos):
        fs = self.app.fs
        dlg = self.app.dialogs
        
        if not fs.preview_active:
            return False
        
        if hasattr(dlg, '_preview_close') and dlg._preview_close.collidepoint(pos):
            fs.close_preview()
            return True
        
        if hasattr(dlg, '_preview_open') and dlg._preview_open.collidepoint(pos):
            try:
                FileOperations().open_file(fs.preview_file_path)
            except:
                pass
            fs.close_preview()
            return True
        
        if hasattr(dlg, '_preview_set') and dlg._preview_set.collidepoint(pos):
            fs.settings_file = fs.preview_file_path
            fs.settings_active = True
            return True
        
        return False
    
    def _check_settings_dialog_click(self, pos):
        fs = self.app.fs
        dlg = self.app.dialogs
        
        if not fs.settings_active:
            return False
        
        if hasattr(dlg, '_settings_close') and dlg._settings_close.collidepoint(pos):
            fs.close_settings()
            return True
        
        if hasattr(dlg, '_settings_btns'):
            for btn, prog in dlg._settings_btns:
                if btn.collidepoint(pos):
                    ext = os.path.splitext(fs.settings_file)[1]
                    fs.associations[ext] = prog
                    fs.close_settings()
                    return True
        
        return False
    
    def _handle_left_click(self, pos):
        fs = self.app.fs
        ui = self.app.ui
        
        if ui.theme_btn and ui.theme_btn.collidepoint(pos):
            self.app.config.toggle_theme()
            return
        
        for i, btn in enumerate(ui.nav_btns):
            if btn.collidepoint(pos):
                if i == 0:
                    fs.go_home()
                elif i == 1:
                    fs.go_up()
                elif i == 2:
                    fs.refresh()
                return
        
        for rect, path in ui.quick_items:
            if rect.collidepoint(pos):
                fs.navigate(path)
                return
        
        self._handle_file_click(pos)
    
    def _handle_right_click(self, pos):
        """处理右键点击"""
        fs = self.app.fs
        mx = self.app.config.sidebar_width
        
        if pos[0] <= mx:
            return  # 在侧边栏区域，不处理
        
        # 先检查是否点击了文件
        list_y = 95
        for i, fi in enumerate(fs.files):
            y = list_y + i * self.app.config.item_height - fs.scroll_offset
            rect = pygame.Rect(mx+10, y, self.app.config.screen_width-mx-25, self.app.config.item_height)
            
            if rect.collidepoint(pos):
                # 点击了文件
                fs.selected_file = fi['path']
                self.context_menu_active = True
                self.context_menu_pos = pos
                self.context_menu_file = fi
                self.context_menu_is_blank = False
                return
            
            # 没有点击文件，点击的是空白处
            self.context_menu_active = True
            self.context_menu_pos = pos
            self.context_menu_file = None
            self.context_menu_is_blank = True
            
    
    def _handle_file_click(self, pos):
        fs = self.app.fs
        mx = self.app.config.sidebar_width
        
        if pos[0] <= mx:
            return
        
        list_y = 95
        for i, fi in enumerate(fs.files):
            y = list_y + i * self.app.config.item_height - fs.scroll_offset
            rect = pygame.Rect(mx+10, y, self.app.config.screen_width-mx-25, self.app.config.item_height)
            
            if rect.collidepoint(pos):
                if fs.selected_file == fi['path']:
                    fs.open_selected()
                else:
                    fs.selected_file = fi['path']
                return
    
    def _scroll(self, amount):
        fs = self.app.fs
        fs.target_scroll += amount
        fs.target_scroll = max(0, min(fs.max_scroll, fs.target_scroll))
    
    def _handle_key(self, event):
        fs = self.app.fs
        
        if hasattr(self.app, 'create_dialog') and self.app.create_dialog.is_active():
            self.app.create_dialog.handle_key(event)
            return
        
        if hasattr(self.app, 'rename_dialog') and self.app.rename_dialog.is_active():
            self.app.rename_dialog.handle_key(event)
            return
        
        if hasattr(self.app, 'txt_edit_dialog') and self.app.txt_edit_dialog.is_active():
            self.app.txt_edit_dialog.handle_key(event)
            return
        
        if hasattr(self.app, 'crypto_dialog') and self.app.crypto_dialog:
            crypto = self.app.crypto_dialog
            is_active = crypto.is_active() if callable(getattr(crypto, 'is_active', None)) else crypto.active
            if is_active and hasattr(crypto, 'handle_key'):
                if crypto.handle_key(event):
                    return
        
        if event.key == pygame.K_ESCAPE:
            if fs.settings_active:
                fs.close_settings()
            elif fs.preview_active:
                fs.close_preview()
        elif event.key == pygame.K_F5:
            fs.refresh()
        elif event.key == pygame.K_BACKSPACE:
            fs.go_up()
        elif event.key == pygame.K_RETURN:
            fs.open_selected()
        elif event.key == pygame.K_HOME:
            fs.go_home()
        elif event.key == pygame.K_LEFT:
            fs.go_back()
        elif event.key == pygame.K_RIGHT:
            fs.go_forward()
        elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Ctrl+N 新建文件
            if hasattr(self.app, 'create_dialog') and self.app.create_dialog:
                self.app.create_dialog.show(self.app.fs.current_path)
    
    # ===== 右键菜单动作 =====
    
    def _menu_encrypt(self, file_info):
        if hasattr(self.app, 'crypto_dialog') and self.app.crypto_dialog is not None:
            self.app.crypto_dialog.show_encrypt(file_info['path'])
    
    def _menu_decrypt(self, file_info):
        if hasattr(self.app, 'crypto_dialog') and self.app.crypto_dialog is not None:
            self.app.crypto_dialog.show_decrypt(file_info['path'])
    
    def _menu_open_with(self, file_info):
        self.app.fs.settings_file = file_info['path']
        self.app.fs.settings_active = True
    
    def _menu_copy_path(self, file_info):
        try:
            import pyperclip
            pyperclip.copy(file_info['path'])
        except ImportError:
            pass
    
    def _menu_properties(self, file_info):
        info = f"名称: {file_info['name']}\n"
        info += f"大小: {FileOperations.format_size(file_info['size'])}\n"
        info += f"修改时间: {FileOperations.format_date(file_info['modified'])}"
        print(info)
    
    def _menu_delete(self, file_info):
        import shutil
        try:
            path = file_info['path']
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.app.fs.refresh()
        except Exception as e:
            print(f"删除失败: {e}")
    
    def _menu_new_file(self, file_info=None):
        """新建文件"""
        if hasattr(self.app, 'create_dialog') and self.app.create_dialog:
            self.app.create_dialog.show(self.app.fs.current_path)
    
    def _menu_new_folder(self):
        """新建文件夹"""
        try:
            folder_name = "新建文件夹"
            folder_path = os.path.join(self.app.fs.current_path, folder_name)
            counter = 1
            while os.path.exists(folder_path):
                folder_path = os.path.join(self.app.fs.current_path, f"{folder_name}_{counter}")
                counter += 1
            os.makedirs(folder_path)
            self.app.fs.refresh()
        except Exception as e:
            print(f"创建文件夹失败: {e}")
    
    def _menu_rename_file(self, file_info):
        """重命名文件"""
        if hasattr(self.app, 'rename_dialog') and self.app.rename_dialog:
            self.app.rename_dialog.show(file_info['path'])
    
    def _menu_edit_file(self, file_info):
        """编辑txt文件"""
        if hasattr(self.app, 'txt_edit_dialog') and self.app.txt_edit_dialog:
            self.app.txt_edit_dialog.show(file_info['path'])
    
    def _menu_create_txt(self):
        from file_editor import FileCreator
        path = FileCreator.create_txt(self.app.fs.current_path)
        self.app.fs.refresh()
    
    def _menu_create_png(self):
        from file_editor import FileCreator
        path = FileCreator.create_png(filename="新建图片.png")
        self.app.fs.refresh()
    
    def _menu_create_jpg(self):
        from file_editor import FileCreator
        path = FileCreator.create_jpg(filename="新建图片.jpg")
        self.app.fs.refresh()
    
    def _menu_create_bmp(self):
        from file_editor import FileCreator
        path = FileCreator.create_bmp(filename="新建图片.bmp")
        self.app.fs.refresh()
    
    def _menu_create_mth(self):
        from file_editor import FileCreator
        path = FileCreator.create_math_image(filename="数学图像.mth")
        self.app.fs.refresh()
    
    def _menu_create_py(self):
        path = os.path.join(self.app.fs.current_path, "新建脚本.py")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(self.app.fs.current_path, f"新建脚本_{counter}.py")
            counter += 1
        with open(path, 'w', encoding='utf-8') as f:
            f.write('#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n')
            f.write('def main():\n    print("Hello, World!")\n\n')
            f.write('if __name__ == "__main__":\n    main()\n')
        self.app.fs.refresh()
    
    def _menu_create_js(self):
        path = os.path.join(self.app.fs.current_path, "新建脚本.js")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(self.app.fs.current_path, f"新建脚本_{counter}.js")
            counter += 1
        with open(path, 'w', encoding='utf-8') as f:
            f.write('// JavaScript File\n\n')
            f.write('function main() {\n    console.log("Hello, World!");\n}\n\n')
            f.write('main();\n')
        self.app.fs.refresh()
    
    def _menu_create_vbs(self):
        path = os.path.join(self.app.fs.current_path, "新建脚本.vbs")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(self.app.fs.current_path, f"新建脚本_{counter}.vbs")
            counter += 1
        with open(path, 'w', encoding='utf-8') as f:
            f.write('MsgBox "Hello, World!", vbInformation, "VBScript"\n')
        self.app.fs.refresh()
    
    def _menu_create_cpp(self):
        path = os.path.join(self.app.fs.current_path, "新建代码.cpp")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(self.app.fs.current_path, f"新建代码_{counter}.cpp")
            counter += 1
        with open(path, 'w', encoding='utf-8') as f:
            f.write('#include <iostream>\n\n')
            f.write('int main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}\n')
        self.app.fs.refresh()
    
    def _menu_create_c(self):
        path = os.path.join(self.app.fs.current_path, "新建代码.c")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(self.app.fs.current_path, f"新建代码_{counter}.c")
            counter += 1
        with open(path, 'w', encoding='utf-8') as f:
            f.write('#include <stdio.h>\n\n')
            f.write('int main() {\n    printf("Hello, World!\\n");\n    return 0;\n}\n')
        self.app.fs.refresh()