"""
自动加密系统 - 根据文件大小自动选择密钥强度
生成二维码密钥并保存，加密文件后缀为 .de
"""
import os
import json
import base64
import hashlib
import secrets
import qrcode
from PIL import Image
import io
import pygame
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class AdaptiveKeyGenerator:
    """根据文件大小自动选择合适密钥强度"""
    
    # 密钥强度配置
    KEY_CONFIGS = {
        'light': {  # 小文件 < 1MB
            'curve': ec.SECP256R1(),
            'aes_key_size': 16,  # AES-128
            'name': 'AES-128 + ECC-P256'
        },
        'standard': {  # 中等文件 1MB - 100MB
            'curve': ec.SECP384R1(),
            'aes_key_size': 24,  # AES-192
            'name': 'AES-192 + ECC-P384'
        },
        'strong': {  # 大文件 > 100MB
            'curve': ec.SECP521R1(),
            'aes_key_size': 32,  # AES-256
            'name': 'AES-256 + ECC-P521'
        },
    }
    
    @staticmethod
    def get_key_config(file_size):
        """根据文件大小选择密钥配置"""
        if file_size < 1024 * 1024:  # < 1MB
            return AdaptiveKeyGenerator.KEY_CONFIGS['light']
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            return AdaptiveKeyGenerator.KEY_CONFIGS['standard']
        else:  # >= 100MB
            return AdaptiveKeyGenerator.KEY_CONFIGS['strong']
    
    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"


class FileEncryptor:
    """文件加密器 - 生成.de后缀文件"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.key_config = None
    
    def generate_keys(self, file_size):
        """根据文件大小生成密钥对"""
        self.key_config = AdaptiveKeyGenerator.get_key_config(file_size)
        
        # 生成ECC密钥对
        self.private_key = ec.generate_private_key(
            self.key_config['curve'], 
            default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        return self.get_public_key_pem(), self.get_private_key_pem()
    
    def get_public_key_pem(self):
        """获取公钥PEM"""
        if self.public_key:
            return self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
        return None
    
    def get_private_key_pem(self):
        """获取私钥PEM"""
        if self.private_key:
            return self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
        return None
    
    def encrypt_file(self, file_path, output_dir=None, progress_callback=None):
        """加密文件，生成.de文件"""
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        if progress_callback:
            progress_callback(0, "正在分析文件...")
        
        # 生成密钥
        public_pem, private_pem = self.generate_keys(file_size)
        
        if progress_callback:
            progress_callback(10, "正在生成密钥...")
        
        # 读取文件
        with open(file_path, 'rb') as f:
            plaintext = f.read()
        
        if progress_callback:
            progress_callback(20, "正在加密文件...")
        
        # 生成临时密钥对用于ECDH
        ephemeral_private = ec.generate_private_key(
            self.key_config['curve'], 
            default_backend()
        )
        ephemeral_public = ephemeral_private.public_key()
        
        # ECDH密钥交换
        shared_key = ephemeral_private.exchange(ec.ECDH(), self.public_key)
        
        if progress_callback:
            progress_callback(40, "正在派生加密密钥...")
        
        # 派生AES密钥
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=self.key_config['aes_key_size'],
            salt=None,
            info=b'file-encryption-v2',
            backend=default_backend()
        ).derive(shared_key)
        
        # AES-GCM加密
        iv = secrets.token_bytes(12)
        cipher = Cipher(
            algorithms.AES(derived_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # 分块加密大文件
        chunk_size = 1024 * 1024  # 1MB 块
        ciphertext = bytearray()
        
        for i in range(0, len(plaintext), chunk_size):
            chunk = plaintext[i:i+chunk_size]
            ciphertext.extend(encryptor.update(chunk))
            
            if progress_callback and len(plaintext) > chunk_size:
                progress = 40 + int((i / len(plaintext)) * 40)
                progress_callback(progress, f"正在加密... {min(100, progress)}%")
        
        ciphertext.extend(encryptor.finalize())
        tag = encryptor.tag
        
        if progress_callback:
            progress_callback(85, "正在生成加密文件...")
        
        # 序列化临时公钥
        ephemeral_public_bytes = ephemeral_public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # 计算文件哈希
        file_hash = hashlib.sha256(plaintext).hexdigest()
        
        # 构建加密文件头
        header = {
            'version': '2.0',
            'original_name': file_name,
            'original_size': file_size,
            'key_strength': self.key_config['name'],
            'file_hash': file_hash,
            'ephemeral_public_key': ephemeral_public_bytes.decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8'),
        }
        
        header_json = json.dumps(header, indent=2)
        header_bytes = header_json.encode('utf-8')
        header_length = len(header_bytes).to_bytes(4, 'big')
        
        # 生成.de文件路径
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, file_name + '.de')
        else:
            output_path = file_path + '.de'
        
        # 写入加密文件
        with open(output_path, 'wb') as f:
            f.write(b'DE01')  # 文件签名
            f.write(header_length)  # 头部长度
            f.write(header_bytes)  # JSON头部
            f.write(bytes(ciphertext))  # 加密内容
        
        if progress_callback:
            progress_callback(100, "加密完成!")
        
        return output_path, private_pem
    
    def decrypt_file(self, file_path, private_key_pem, output_dir=None, progress_callback=None):
        """解密.de文件，恢复原始文件名和后缀"""
        if not file_path.endswith('.de'):
            raise ValueError("不是有效的.de加密文件")
        
        if progress_callback:
            progress_callback(0, "正在读取加密文件...")
        
        # 读取加密文件
        with open(file_path, 'rb') as f:
            signature = f.read(4)
            if signature != b'DE01':
                raise ValueError("文件格式不正确")
            
            header_length = int.from_bytes(f.read(4), 'big')
            header_bytes = f.read(header_length)
            ciphertext = f.read()
        
        if progress_callback:
            progress_callback(10, "正在解析文件头...")
        
        # 解析头部
        header = json.loads(header_bytes.decode('utf-8'))
        
        # 获取原始文件名（包含原始后缀）
        original_name = header.get('original_name', 'decrypted_file')
        
        # 加载私钥
        if isinstance(private_key_pem, str):
            private_key_pem = private_key_pem.encode('utf-8')
        
        private_key = serialization.load_pem_private_key(
            private_key_pem, 
            password=None, 
            backend=default_backend()
        )
        
        if progress_callback:
            progress_callback(20, "正在解密...")
        
        # 加载临时公钥
        ephemeral_public_bytes = header['ephemeral_public_key'].encode('utf-8')
        ephemeral_public = serialization.load_pem_public_key(
            ephemeral_public_bytes, 
            backend=default_backend()
        )
        
        # ECDH密钥交换
        shared_key = private_key.exchange(ec.ECDH(), ephemeral_public)
        
        # 派生AES密钥
        key_strength = header.get('key_strength', '')
        if '128' in key_strength:
            aes_key_size = 16
        elif '192' in key_strength:
            aes_key_size = 24
        else:
            aes_key_size = 32
        
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=aes_key_size,
            salt=None,
            info=b'file-encryption-v2',
            backend=default_backend()
        ).derive(shared_key)
        
        # AES-GCM解密
        iv = base64.b64decode(header['iv'])
        tag = base64.b64decode(header['tag'])
        
        cipher = Cipher(
            algorithms.AES(derived_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # 分块解密
        chunk_size = 1024 * 1024
        plaintext = bytearray()
        
        for i in range(0, len(ciphertext), chunk_size):
            chunk = ciphertext[i:i+chunk_size]
            plaintext.extend(decryptor.update(chunk))
            
            if progress_callback and len(ciphertext) > chunk_size:
                progress = 30 + int((i / len(ciphertext)) * 60)
                progress_callback(progress, f"正在解密... {min(100, progress)}%")
        
        plaintext.extend(decryptor.finalize())
        
        if progress_callback:
            progress_callback(95, "正在验证文件完整性...")
        
        # 验证哈希
        computed_hash = hashlib.sha256(plaintext).hexdigest()
        if computed_hash != header.get('file_hash', ''):
            raise ValueError("文件完整性验证失败！密钥可能不正确")
        
        # ===== 关键修改：使用原始文件名作为输出 =====
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, original_name)
        else:
            # 默认输出到加密文件所在目录，使用原始文件名
            parent_dir = os.path.dirname(file_path)
            output_path = os.path.join(parent_dir, original_name)
        
        # 如果文件已存在，添加序号
        if os.path.exists(output_path):
            base, ext = os.path.splitext(original_name)
            counter = 1
            while True:
                new_name = f"{base}_{counter}{ext}"
                new_path = os.path.join(
                    output_dir if output_dir else parent_dir, 
                    new_name
                )
                if not os.path.exists(new_path):
                    output_path = new_path
                    break
                counter += 1
        
        # 写入解密文件
        with open(output_path, 'wb') as f:
            f.write(bytes(plaintext))
        
        if progress_callback:
            progress_callback(100, f"解密完成! 文件: {original_name}")
        
        return output_path


class QRKeyManager:
    """二维码密钥管理器"""
    
    @staticmethod
    def generate_key_qr(key_data, file_name, key_type='private', save_dir=None):
        """生成密钥二维码并保存"""
        # 构建二维码数据
        qr_data = json.dumps({
            'type': key_type,
            'file': file_name,
            'key': key_data,
            'version': '2.0'
        })
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # 创建图像
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # 添加标签
        from PIL import ImageDraw, ImageFont
        qr_width, qr_height = qr_image.size
        
        # 创建带标签的新图像
        label_height = 80
        new_image = Image.new('RGB', (qr_width, qr_height + label_height), 'white')
        new_image.paste(qr_image, (0, 0))
        
        # 添加文字标签
        draw = ImageDraw.Draw(new_image)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        label_text = f"File: {file_name}\nKey: {key_type.upper()}"
        draw.text((10, qr_height + 10), label_text, fill='black', font=font)
        
        # 保存二维码
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            safe_name = "".join(c for c in file_name if c.isalnum() or c in '._-')
            qr_path = os.path.join(save_dir, f"{safe_name}_{key_type}_key.png")
        else:
            qr_path = f"{file_name}_{key_type}_key.png"
        
        new_image.save(qr_path)
        return qr_path, qr_data
    
    @staticmethod
    def decode_qr_image(image_path):
        """从二维码图片解码密钥"""
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image as PILImage
            
            image = PILImage.open(image_path)
            decoded_objects = decode(image)
            
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                try:
                    parsed = json.loads(data)
                    if 'key' in parsed:
                        return parsed
                except:
                    pass
            
            return None
        except ImportError:
            print("需要安装 pyzbar: pip install pyzbar")
            return None
    
    @staticmethod
    def decode_qr_from_camera():
        """从摄像头扫描二维码"""
        try:
            import cv2
            from pyzbar.pyzbar import decode
            import numpy as np
            
            cap = cv2.VideoCapture(0)
            print("正在打开摄像头... 按 'q' 退出")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                decoded_objects = decode(frame)
                
                for obj in decoded_objects:
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(
                            np.array([p for p in points], dtype=np.float32)
                        )
                        cv2.polylines(frame, [hull.astype(np.int32)], True, (0, 255, 0), 2)
                    
                    data = obj.data.decode('utf-8')
                    try:
                        parsed = json.loads(data)
                        if 'key' in parsed:
                            cap.release()
                            cv2.destroyAllWindows()
                            return parsed
                    except:
                        pass
                
                cv2.imshow('Scan QR Code - Press Q to quit', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            return None
        except ImportError:
            print("需要安装 opencv-python: pip install opencv-python")
            return None
    
    @staticmethod
    def qr_to_pygame_surface(qr_image, max_size=400):
        """将二维码转换为Pygame表面"""
        # 调整大小
        w, h = qr_image.size
        if w > max_size or h > max_size:
            ratio = max_size / max(w, h)
            new_size = (int(w * ratio), int(h * ratio))
            qr_image = qr_image.resize(new_size, Image.LANCZOS)
        
        # 转换为RGB
        if qr_image.mode != 'RGB':
            qr_image = qr_image.convert('RGB')
        
        # 转换为Pygame表面
        data = qr_image.tobytes()
        size = qr_image.size
        return pygame.image.fromstring(data, size, 'RGB')


class CryptoDialog:
    """加密对话框"""
    
    def __init__(self, screen, config, fonts):
        self.screen = screen
        self.config = config
        self.fonts = fonts
        self.encryptor = FileEncryptor()
        self.qr_manager = QRKeyManager()
        
        # 状态
        self.active = False
        self.mode = None  # 'encrypt' or 'decrypt'
        self.file_path = None
        self.status_text = ""
        self.progress = 0
        
        # 二维码显示
        self.showing_qr = False
        self.qr_surface = None
        self.qr_path = None
        
        # 动画
        self.dialog_scale = 0.8
        self.overlay_alpha = 0
        
        # 按钮
        self.buttons = []
        self.close_btn = None
        
        # 保存目录
        self.save_dir = os.path.expanduser("~/Desktop/密钥二维码")
    
    def show_encrypt(self, file_path):
        """显示加密对话框"""
        self.active = True
        self.mode = 'encrypt'
        self.file_path = file_path
        self.status_text = f"准备加密: {os.path.basename(file_path)}"
        self.progress = 0
        self.showing_qr = False
        self.reset_animation()
        self._start_encryption()
    
    def show_decrypt(self, file_path):
        """显示解密对话框"""
        self.active = True
        self.mode = 'decrypt'
        self.file_path = file_path
        self.status_text = "请导入私钥二维码"
        self.progress = 0
        self.showing_qr = False
        self.reset_animation()
    
    def _start_encryption(self):
        """开始加密"""
        try:
            file_size = os.path.getsize(self.file_path)
            key_config = AdaptiveKeyGenerator.get_key_config(file_size)
            
            self.status_text = f"文件大小: {AdaptiveKeyGenerator.format_size(file_size)}\n密钥强度: {key_config['name']}"
            
            # 执行加密
            output_path, private_pem = self.encryptor.encrypt_file(
                self.file_path,
                progress_callback=self._update_progress
            )
            
            # 生成私钥二维码
            self.status_text = "正在生成密钥二维码..."
            file_name = os.path.basename(self.file_path)
            qr_path, qr_data = self.qr_manager.generate_key_qr(
                private_pem, file_name, 'private', self.save_dir
            )
            
            self.qr_path = qr_path
            self.status_text = f"加密完成!\n加密文件: {os.path.basename(output_path)}\n密钥二维码已保存至: {qr_path}"
            
            # 加载二维码显示
            qr_image = Image.open(qr_path)
            self.qr_surface = self.qr_manager.qr_to_pygame_surface(qr_image, 300)
            self.showing_qr = True
            
        except Exception as e:
            self.status_text = f"加密失败: {str(e)}"
    
    def _update_progress(self, progress, status):
        """更新进度"""
        self.progress = progress
        self.status_text = status
    
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
            
            # 白色背景
            qr_bg = pygame.Rect(qr_x-10, qr_y-10, 
                               self.qr_surface.get_width()+20, 
                               self.qr_surface.get_height()+20)
            pygame.draw.rect(self.screen, (255, 255, 255), qr_bg, border_radius=5)
            self.screen.blit(self.qr_surface, (qr_x, qr_y))
            
            content_y = qr_y + self.qr_surface.get_height() + 15
        
        # 状态文本
        for i, line in enumerate(self.status_text.split('\n')):
            txt_surf = self.fonts.render(line, 'small', c['text'])
            self.screen.blit(txt_surf, (ax+30, content_y + i*25))
            content_y += 25
        
        # 进度条
        if self.progress < 100:
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
        
        if self.mode == 'decrypt':
            # 扫描二维码按钮
            scan_btn = pygame.Rect(ax+30, btn_y, 160, 35)
            is_hover = scan_btn.collidepoint(pygame.mouse.get_pos())
            bg = c['accent_hover'] if is_hover else c['accent']
            pygame.draw.rect(self.screen, bg, scan_btn, border_radius=6)
            scan_txt = self.fonts.render("扫描二维码", 'small', (255,255,255))
            self.screen.blit(scan_txt, (scan_btn.x+20, scan_btn.y+8))
            self.buttons.append((scan_btn, self._scan_qr_decrypt))
            
            # 导入二维码图片按钮
            import_btn = pygame.Rect(ax+210, btn_y, 160, 35)
            is_hover = import_btn.collidepoint(pygame.mouse.get_pos())
            bg = c['accent_hover'] if is_hover else c['accent']
            pygame.draw.rect(self.screen, bg, import_btn, border_radius=6)
            import_txt = self.fonts.render("导入二维码", 'small', (255,255,255))
            self.screen.blit(import_txt, (import_btn.x+20, import_btn.y+8))
            self.buttons.append((import_btn, self._import_qr_decrypt))
    
    def _scan_qr_decrypt(self):
        """扫描二维码解密"""
        result = self.qr_manager.decode_qr_from_camera()
        if result and 'key' in result:
            self._decrypt_with_key(result['key'])
        else:
            self.status_text = "未检测到有效的二维码"
    
    def _import_qr_decrypt(self):
        """导入二维码图片解密"""
        from tkinter import filedialog
        image_path = filedialog.askopenfilename(
            title="选择私钥二维码图片",
            filetypes=[("PNG images", "*.png"), ("All files", "*.*")]
        )
        
        if image_path:
            result = self.qr_manager.decode_qr_image(image_path)
            if result and 'key' in result:
                self._decrypt_with_key(result['key'])
            else:
                self.status_text = "无法从图片中读取密钥"
    
    def _decrypt_with_key(self, private_key_pem):
        """使用私钥解密"""
        try:
            self.status_text = "正在解密..."
            self.progress = 0
            
            output_path = self.encryptor.decrypt_file(
                self.file_path,
                private_key_pem,
                progress_callback=self._update_progress
            )
            
            self.status_text = f"解密完成!\n文件已保存至: {output_path}"
            self.progress = 100
            
        except Exception as e:
            self.status_text = f"解密失败: {str(e)}"
    
    def handle_click(self, pos):
        """处理点击"""
        if self.close_btn and self.close_btn.collidepoint(pos):
            self.active = False
            return True
        
        for btn_rect, action in self.buttons:
            if btn_rect.collidepoint(pos):
                action()
                return True
        
        return False
    
    def is_active(self):
        return self.active