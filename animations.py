"""
动画系统模块
提供流畅的动画效果：缓动函数、过渡动画、弹簧动画等
"""

import math
import time

class Easing:
    """缓动函数集合"""
    
    @staticmethod
    def linear(t):
        return t
    
    @staticmethod
    def ease_in_quad(t):
        return t * t
    
    @staticmethod
    def ease_out_quad(t):
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t):
        if t < 0.5:
            return 2 * t * t
        return -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t):
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t):
        t -= 1
        return t * t * t + 1
    
    @staticmethod
    def ease_in_out_cubic(t):
        if t < 0.5:
            return 4 * t * t * t
        t -= 1
        return 4 * t * t * t + 1
    
    @staticmethod
    def ease_in_quart(t):
        return t * t * t * t
    
    @staticmethod
    def ease_out_quart(t):
        t -= 1
        return -(t * t * t * t - 1)
    
    @staticmethod
    def ease_in_out_quart(t):
        if t < 0.5:
            return 8 * t * t * t * t
        t -= 1
        return -8 * t * t * t * t + 1
    
    @staticmethod
    def ease_in_quint(t):
        return t * t * t * t * t
    
    @staticmethod
    def ease_out_quint(t):
        t -= 1
        return t * t * t * t * t + 1
    
    @staticmethod
    def ease_in_out_quint(t):
        if t < 0.5:
            return 16 * t * t * t * t * t
        t -= 1
        return 16 * t * t * t * t * t + 1
    
    @staticmethod
    def ease_in_sine(t):
        return 1 - math.cos(t * math.pi / 2)
    
    @staticmethod
    def ease_out_sine(t):
        return math.sin(t * math.pi / 2)
    
    @staticmethod
    def ease_in_out_sine(t):
        return -(math.cos(math.pi * t) - 1) / 2
    
    @staticmethod
    def ease_in_expo(t):
        if t == 0:
            return 0
        return math.pow(2, 10 * (t - 1))
    
    @staticmethod
    def ease_out_expo(t):
        if t == 1:
            return 1
        return 1 - math.pow(2, -10 * t)
    
    @staticmethod
    def ease_in_out_expo(t):
        if t == 0 or t == 1:
            return t
        if t < 0.5:
            return math.pow(2, 20 * t - 10) / 2
        return (2 - math.pow(2, -20 * t + 10)) / 2
    
    @staticmethod
    def ease_out_back(t):
        c1 = 1.70158
        c3 = c1 + 1
        t -= 1
        return c3 * t * t * t + c1 * t * t + 1
    
    @staticmethod
    def ease_in_out_back(t):
        c1 = 1.70158
        c2 = c1 * 1.525
        if t < 0.5:
            return (2 * t * 2 * t * ((c2 + 1) * 2 * t - c2)) / 2
        t -= 1
        return (4 * t * t * ((c2 + 1) * 2 * t + c2) + 2) / 2
    
    @staticmethod
    def ease_out_elastic(t):
        if t == 0 or t == 1:
            return t
        c4 = (2 * math.pi) / 3
        t -= 1
        return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
    
    @staticmethod
    def ease_out_bounce(t):
        n1 = 7.5625
        d1 = 2.75
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375


class Animation:
    """单个动画对象"""
    
    def __init__(self, start_value, end_value, duration, easing=Easing.ease_out_cubic):
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration  # 秒
        self.easing = easing
        self.start_time = time.time()
        self.finished = False
    
    def get_value(self):
        """获取当前动画值"""
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.finished = True
            return self.end_value
        
        t = elapsed / self.duration
        t = self.easing(t)
        
        if isinstance(self.start_value, (int, float)):
            return self.start_value + (self.end_value - self.start_value) * t
        elif isinstance(self.start_value, tuple):
            return tuple(
                self.start_value[i] + (self.end_value[i] - self.start_value[i]) * t
                for i in range(len(self.start_value))
            )
        return self.end_value
    
    def is_finished(self):
        return self.finished


class AnimationManager:
    """动画管理器"""
    
    def __init__(self):
        self.animations = []
    
    def animate(self, target, property_name, start_value, end_value, duration, easing=Easing.ease_out_cubic):
        """创建属性动画"""
        anim = PropertyAnimation(target, property_name, start_value, end_value, duration, easing)
        self.animations.append(anim)
        return anim
    
    def animate_float(self, start_value, end_value, duration, easing=Easing.ease_out_cubic):
        """创建浮点数动画"""
        anim = Animation(start_value, end_value, duration, easing)
        self.animations.append(anim)
        return anim
    
    def update(self):
        """更新所有动画"""
        self.animations = [anim for anim in self.animations if not anim.is_finished()]
    
    def clear(self):
        """清除所有动画"""
        self.animations.clear()


class PropertyAnimation(Animation):
    """属性动画 - 直接修改对象属性"""
    
    def __init__(self, target, property_name, start_value, end_value, duration, easing=Easing.ease_out_cubic):
        super().__init__(start_value, end_value, duration, easing)
        self.target = target
        self.property_name = property_name
    
    def get_value(self):
        value = super().get_value()
        setattr(self.target, self.property_name, value)
        return value


class SmoothValue:
    """平滑值 - 使用弹簧物理的平滑过渡"""
    
    def __init__(self, initial_value=0, stiffness=0.1, damping=0.3):
        self.current = initial_value
        self.target = initial_value
        self.velocity = 0
        self.stiffness = stiffness
        self.damping = damping
    
    def set_target(self, value):
        self.target = value
    
    def set_current(self, value):
        self.current = value
        self.velocity = 0
    
    def update(self, dt=0.016):
        """更新平滑值（使用弹簧物理）"""
        force = (self.target - self.current) * self.stiffness
        self.velocity += force
        self.velocity *= (1 - self.damping)
        self.current += self.velocity
        
        # 如果非常接近目标，直接设置
        if abs(self.target - self.current) < 0.001 and abs(self.velocity) < 0.001:
            self.current = self.target
            self.velocity = 0
    
    def get_value(self):
        return self.current


class ColorAnimation:
    """颜色过渡动画"""
    
    def __init__(self, start_color, end_color, duration, easing=Easing.ease_out_cubic):
        self.start_color = start_color
        self.end_color = end_color
        self.duration = duration
        self.easing = easing
        self.start_time = time.time()
        self.finished = False
    
    def get_color(self):
        """获取当前颜色"""
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.finished = True
            return self.end_color
        
        t = elapsed / self.duration
        t = self.easing(t)
        
        return tuple(
            int(self.start_color[i] + (self.end_color[i] - self.start_color[i]) * t)
            for i in range(min(len(self.start_color), len(self.end_color)))
        )
    
    def is_finished(self):
        return self.finished


class FadeAnimation:
    """淡入淡出动画"""
    
    def __init__(self, fade_in=True, duration=0.3, easing=Easing.ease_out_cubic):
        self.fade_in = fade_in
        self.duration = duration
        self.easing = easing
        self.start_time = time.time()
        self.finished = False
        self.alpha = 0 if fade_in else 255
    
    def get_alpha(self):
        """获取当前透明度"""
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.finished = True
            return 255 if self.fade_in else 0
        
        t = elapsed / self.duration
        t = self.easing(t)
        
        if self.fade_in:
            return int(255 * t)
        else:
            return int(255 * (1 - t))
    
    def is_finished(self):
        return self.finished


class ScaleAnimation:
    """缩放动画"""
    
    def __init__(self, start_scale=0.8, end_scale=1.0, duration=0.3, easing=Easing.ease_out_back):
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.duration = duration
        self.easing = easing
        self.start_time = time.time()
        self.finished = False
    
    def get_scale(self):
        """获取当前缩放值"""
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.finished = True
            return self.end_scale
        
        t = elapsed / self.duration
        t = self.easing(t)
        return self.start_scale + (self.end_scale - self.start_scale) * t
    
    def is_finished(self):
        return self.finished

class ThemeTransition:
    """主题切换过渡动画"""
    
    def __init__(self, duration=0.5):
        self.duration = duration
        self.progress = 0.0
        self.active = False
        self.start_time = 0
    
    def start(self):
        self.active = True
        self.progress = 0.0
        self.start_time = time.time()
    
    def update(self):
        if not self.active:
            return
        
        elapsed = time.time() - self.start_time
        self.progress = min(1.0, elapsed / self.duration)
        
        # 使用缓动函数
        self.progress = Easing.ease_in_out_cubic(self.progress)
        
        if self.progress >= 1.0:
            self.active = False
            self.progress = 1.0
    
    def get_progress(self):
        return self.progress
    
    def is_active(self):
        return self.active

class SlideAnimation:
    """滑动动画"""
    
    def __init__(self, start_pos, end_pos, duration=0.3, easing=Easing.ease_out_cubic):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.easing = easing
        self.start_time = time.time()
        self.finished = False
    
    def get_position(self):
        """获取当前位置"""
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.finished = True
            return self.end_pos
        
        t = elapsed / self.duration
        t = self.easing(t)
        
        return (
            self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t,
            self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        )
    
    def is_finished(self):
        return self.finished
