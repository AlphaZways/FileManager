"""
ECC加密管理模块
使用椭圆曲线加密算法，支持二维码密钥传输
"""
import os
import base64
import json
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
import secrets

class ECCKeyManager:
    """ECC密钥管理器"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.public_bytes = None
        self.private_bytes = None
    
    def generate_key_pair(self):
        """生成ECC密钥对（使用SECP256R1曲线）"""
        self.private_key = ec.generate_private_key(
            ec.SECP256R1(), default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # 序列化公钥
        self.public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # 序列化私钥
        self.private_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return self.public_bytes, self.private_bytes
    
    def get_public_key_pem(self):
        """获取公钥PEM格式字符串"""
        if self.public_bytes:
            return self.public_bytes.decode('utf-8')
        return None
    
    def get_private_key_pem(self):
        """获取私钥PEM格式字符串"""
        if self.private_bytes:
            return self.private_bytes.decode('utf-8')
        return None
    
    def load_public_key(self, pem_data):
        """从PEM加载公钥"""
        if isinstance(pem_data, str):
            pem_data = pem_data.encode('utf-8')
        self.public_key = serialization.load_pem_public_key(
            pem_data, backend=default_backend()
        )
        self.public_bytes = pem_data
    
    def load_private_key(self, pem_data):
        """从PEM加载私钥"""
        if isinstance(pem_data, str):
            pem_data = pem_data.encode('utf-8')
        self.private_key = serialization.load_pem_private_key(
            pem_data, password=None, backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.private_bytes = pem_data
    
    def export_key_pair(self):
        """导出密钥对为JSON"""
        return {
            'public_key': self.get_public_key_pem(),
            'private_key': self.get_private_key_pem(),
            'curve': 'SECP256R1'
        }
    
    def import_key_pair(self, data):
        """从JSON导入密钥对"""
        if isinstance(data, str):
            data = json.loads(data)
        self.load_public_key(data['public_key'])
        self.load_private_key(data['private_key'])


class ECCEncryptor:
    """ECC加密器 - 使用ECIES方案"""
    
    def __init__(self, key_manager=None):
        self.key_manager = key_manager or ECCKeyManager()
    
    def encrypt_file(self, file_path, output_path=None, public_key_pem=None):
        """使用ECC公钥加密文件"""
        if public_key_pem:
            if isinstance(public_key_pem, str):
                public_key_pem = public_key_pem.encode('utf-8')
            public_key = serialization.load_pem_public_key(
                public_key_pem, backend=default_backend()
            )
        else:
            public_key = self.key_manager.public_key
        
        if not public_key:
            raise ValueError("没有可用的公钥")
        
        # 读取文件内容
        with open(file_path, 'rb') as f:
            plaintext = f.read()
        
        # 生成临时密钥对用于ECDH
        ephemeral_private_key = ec.generate_private_key(
            ec.SECP256R1(), default_backend()
        )
        ephemeral_public_key = ephemeral_private_key.public_key()
        
        # ECDH密钥交换
        shared_key = ephemeral_private_key.exchange(
            ec.ECDH(), public_key
        )
        
        # 使用HKDF派生AES密钥
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'ecies-file-encryption',
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
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag
        
        # 序列化临时公钥
        ephemeral_public_bytes = ephemeral_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # 组合加密数据
        encrypted_data = {
            'ephemeral_public_key': ephemeral_public_bytes.decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8'),
        }
        
        encrypted_content = json.dumps(encrypted_data, indent=2).encode('utf-8')
        
        # 保存加密文件
        if output_path is None:
            output_path = file_path + '.enc'
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_content)
        
        return output_path
    
    def decrypt_file(self, file_path, output_path=None, private_key_pem=None):
        """使用ECC私钥解密文件"""
        if private_key_pem:
            if isinstance(private_key_pem, str):
                private_key_pem = private_key_pem.encode('utf-8')
            private_key = serialization.load_pem_private_key(
                private_key_pem, password=None, backend=default_backend()
            )
        else:
            private_key = self.key_manager.private_key
        
        if not private_key:
            raise ValueError("没有可用的私钥")
        
        # 读取加密文件
        with open(file_path, 'rb') as f:
            encrypted_content = f.read()
        
        encrypted_data = json.loads(encrypted_content.decode('utf-8'))
        
        # 解析数据
        ephemeral_public_bytes = encrypted_data['ephemeral_public_key'].encode('utf-8')
        iv = base64.b64decode(encrypted_data['iv'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        tag = base64.b64decode(encrypted_data['tag'])
        
        # 加载临时公钥
        ephemeral_public_key = serialization.load_pem_public_key(
            ephemeral_public_bytes, backend=default_backend()
        )
        
        # ECDH密钥交换
        shared_key = private_key.exchange(
            ec.ECDH(), ephemeral_public_key
        )
        
        # 派生AES密钥
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'ecies-file-encryption',
            backend=default_backend()
        ).derive(shared_key)
        
        # AES-GCM解密
        cipher = Cipher(
            algorithms.AES(derived_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 保存解密文件
        if output_path is None:
            if file_path.endswith('.enc'):
                output_path = file_path[:-4]
            else:
                output_path = file_path + '.dec'
        
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        return output_path


class QRCodeManager:
    """二维码管理器"""
    
    @staticmethod
    def generate_qr(data, box_size=10, border=4):
        """生成二维码图片"""
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # 创建二维码图像
        qr_image = qr.make_image(fill_color="black", back_color="white")
        return qr_image
    
    @staticmethod
    def qr_to_pygame_surface(qr_image, size=None):
        """将二维码PIL图像转换为Pygame表面"""
        # 转换为RGB模式
        if qr_image.mode != 'RGB':
            qr_image = qr_image.convert('RGB')
        
        # 调整大小
        if size:
            qr_image = qr_image.resize((size, size), Image.LANCZOS)
        
        # 转换为Pygame表面
        mode = qr_image.mode
        size = qr_image.size
        data = qr_image.tobytes()
        
        pygame_image = pygame.image.fromstring(data, size, mode)
        return pygame_image
    
    @staticmethod
    def generate_key_qr(key_data, key_type='public', box_size=8, border=4):
        """生成密钥二维码"""
        # 添加标识头
        qr_data = json.dumps({
            'type': key_type,
            'key': key_data,
            'algorithm': 'ECC-SECP256R1'
        })
        
        return QRCodeManager.generate_qr(qr_data, box_size, border)
    
    @staticmethod
    def decode_qr_from_image(image_path):
        """从图片文件解码二维码"""
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image as PILImage
            
            image = PILImage.open(image_path)
            decoded_objects = decode(image)
            
            results = []
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                try:
                    parsed = json.loads(data)
                    results.append(parsed)
                except:
                    results.append({'raw': data})
            
            return results
        except ImportError:
            print("需要安装pyzbar库: pip install pyzbar")
            return []
    
    @staticmethod
    def decode_qr_from_surface(pygame_surface):
        """从Pygame表面解码二维码"""
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image as PILImage
            
            # 将Pygame表面转换为PIL图像
            view = pygame.surfarray.array3d(pygame_surface)
            view = view.transpose([1, 0, 2])
            pil_image = PILImage.fromarray(view)
            
            decoded_objects = decode(pil_image)
            
            results = []
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                try:
                    parsed = json.loads(data)
                    results.append(parsed)
                except:
                    results.append({'raw': data})
            
            return results
        except ImportError:
            print("需要安装pyzbar库: pip install pyzbar")
            return []
    
    @staticmethod
    def save_qr_image(qr_image, file_path):
        """保存二维码图片"""
        qr_image.save(file_path)
        return file_path
    
    @staticmethod
    def decode_qr_from_camera():
        """从摄像头解码二维码"""
        try:
            import cv2
            from pyzbar.pyzbar import decode
            
            cap = cv2.VideoCapture(0)
            
            print("正在打开摄像头... 按 'q' 键退出")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 解码二维码
                decoded_objects = decode(frame)
                
                for obj in decoded_objects:
                    # 绘制边框
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                        cv2.polylines(frame, [hull.astype(np.int32)], True, (0, 255, 0), 2)
                    
                    data = obj.data.decode('utf-8')
                    try:
                        parsed = json.loads(data)
                        cap.release()
                        cv2.destroyAllWindows()
                        return parsed
                    except:
                        cap.release()
                        cv2.destroyAllWindows()
                        return {'raw': data}
                
                cv2.imshow('QR Code Scanner - Press Q to quit', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            return None
        except ImportError:
            print("需要安装opencv-python: pip install opencv-python")
            return None