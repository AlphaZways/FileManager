"""
文件管理系统 - 主入口（修复版）
"""
import pygame
import sys
import os

def main():
    """主函数"""
    try:
        # 1. 初始化 Pygame
        pygame.init()
        
        # 2. 创建窗口
        screen_width = 1200
        screen_height = 800
        
        screen = pygame.display.set_mode(
            (screen_width, screen_height),
            pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("文件管理系统 v2.0")
        
        print("✓ Pygame 初始化成功")
        
        # 3. 初始化配置
        from config import Config
        config = Config()
        config.screen_width = screen_width
        config.screen_height = screen_height
        print(f"✓ 配置加载成功，主题: {config.current_theme}")
        
        # 4. 初始化字体
        from fonts import FontManager
        fonts = FontManager()
        print("✓ 字体加载成功")
        
        # 5. 初始化文件系统
        from file_system import FileSystem
        fs = FileSystem(config)
        print(f"✓ 文件系统加载成功，当前路径: {fs.current_path}")
        
        # 6. 初始化UI渲染器
        from ui_renderer import UIRenderer
        ui = UIRenderer(screen, config, fs)
        print("✓ UI渲染器加载成功")
        
        # 7. 初始化对话框
        from dialogs import Dialogs
        dialogs = Dialogs(screen, config, fs)
        print("✓ 对话框加载成功")
        
        # 8. 创建 App 对象
        app = App(screen, config, fs, ui, dialogs)
        print("✓ App 创建成功")
        
        # 9. 初始化加密对话框（关键修复）
        try:
            from crypto_system import CryptoDialog
            app.crypto_dialog = CryptoDialog(screen, config, fonts)
            print("✓ 加密对话框加载成功")
        except Exception as e:
            print(f"✗ 加密模块加载失败: {e}")
            import traceback
            traceback.print_exc()
            # 设置为 None 而不是 False
            app.crypto_dialog = None
        
        # 10. 初始化事件处理器
        from event_handler import EventHandler
        app.event_handler = EventHandler(app)
        print("✓ 事件处理器加载成功")

        from file_editor import CreateFileDialog, RenameDialog, TxtEditDialog
        app.create_dialog = CreateFileDialog(screen, config, fonts)
        app.rename_dialog = RenameDialog(screen, config, fonts)
        app.txt_edit_dialog = TxtEditDialog(screen, config, fonts)
        
        print("\n" + "="*50)
        print("  文件管理系统启动成功！")
        print("="*50 + "\n")
        
        # 11. 运行应用
        app.run()
        
    except Exception as e:
        print(f"\n✗ 程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


class App:
    """应用程序类"""
    
    def __init__(self, screen, config, fs, ui, dialogs):
        self.screen = screen
        self.config = config
        self.fs = fs
        self.ui = ui
        self.dialogs = dialogs
        
        # 明确初始化为 None
        self.crypto_dialog = None
        self.event_handler = None
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def run(self):
        """主循环"""
        while self.running:
            # 处理事件
            if self.event_handler:
                self.event_handler.handle()
            
            # 更新主题过渡动画
            if self.config.theme_transitioning:
                self.config.transition_progress += 0.02
                if self.config.transition_progress >= 1.0:
                    self.config.transition_progress = 1.0
                    self.config.theme_transitioning = False
            
            # 绘制界面
            self.ui.draw_all()
            self.dialogs.draw()
            
            # 绘制右键菜单
            if self.event_handler and self.event_handler.context_menu_active:
                self.ui.draw_context_menu(self.event_handler)
            
            # 绘制加密对话框
            if self.crypto_dialog is not None:
                if self.crypto_dialog.is_active():
                    self.crypto_dialog.draw()

            # 绘制新建/重命名/编辑对话框
            if self.create_dialog and self.create_dialog.is_active():
                self.create_dialog.draw()
            if self.rename_dialog and self.rename_dialog.is_active():
                self.rename_dialog.draw()
            if self.txt_edit_dialog and self.txt_edit_dialog.is_active():
                self.txt_edit_dialog.draw()
            
            # 更新显示
            pygame.display.flip()
            self.clock.tick(60)
        
    
        
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()