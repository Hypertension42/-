import pygame
import os
import sys
import requests
import hashlib
import random
import json
from pygame.locals import *

# 初始化Pygame
pygame.init()
os.environ['SDL_IME_SHOW_UI'] = '1'  # 启用输入法UI显示

# 颜色定义（暗色风格）
BACKGROUND_COLOR = (30, 30, 30)  # 深灰色背景
TEXT_COLOR = (220, 220, 220)  # 浅灰色文字
ACTIVE_COLOR = (100, 149, 237)  # 活跃元素颜色（浅蓝色）
INACTIVE_COLOR = (60, 60, 60)  # 非活跃元素颜色（深灰色）
BUTTON_COLOR = (40, 40, 40)  # 按钮背景颜色
BUTTON_TEXT_COLOR = (220, 220, 220)  # 按钮文字颜色
INPUT_BG_COLOR = (40, 40, 40)  # 输入框背景
OUTPUT_BG_COLOR = (40, 40, 40)  # 输出框背景
ACCENT_COLOR = (100, 149, 237)  # 强调色（用于光标等）

# 创建窗口
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("文言文翻译器")

# 字体
title_font = pygame.font.SysFont('simhei', 48)
button_font = pygame.font.SysFont('simhei', 28)
text_font = pygame.font.SysFont('simhei', 24)

# 百度翻译API配置
APP_ID = '20250327002316332'  # 需替换为实际值
APP_KEY = 'EmMpQqk2wGWUOTy1_EGM'  # 需替换为实际值
BASE_URL = 'https://fanyi-api.baidu.com/api/trans/vip/translate'


class TranslatorGUI:
    def __init__(self):
        self.input_text = ""
        self.output_text = ""
        self.translation_direction = 0  # 0:文言→现代 1:现代→文言
        self.active_input = False
        self.cursor_visible = True
        self.cursor_timer = 0

        # 按钮位置和大小
        button_width = 300
        button_height = 60
        button_spacing = 20
        buttons_start_y = 130  # 将按钮整体上移

        self.buttons = [
            {"rect": pygame.Rect((WIDTH - button_width) // 2, buttons_start_y, button_width, button_height),
             "text": "文言文 → 现代文", "active": True},
            {"rect": pygame.Rect((WIDTH - button_width) // 2, buttons_start_y + button_height + button_spacing,
                                 button_width, button_height), "text": "现代文 → 文言文", "active": False},
            {"rect": pygame.Rect((WIDTH - button_width) // 2, buttons_start_y + 2 * (button_height + button_spacing),
                                 button_width, button_height), "text": "翻译", "active": False}
        ]

        # 输入框和输出框位置和大小
        text_box_width = 600  # 调小宽度
        text_box_height = 200  # 调小高度
        text_box_spacing = 40  # 文本框之间的间距
        text_boxes_start_y = 400  # 输入框的起始位置

        self.input_rect = pygame.Rect((WIDTH - text_box_width) // 2, text_boxes_start_y, text_box_width,
                                      text_box_height)
        self.output_rect = pygame.Rect((WIDTH - text_box_width) // 2,
                                       text_boxes_start_y + text_box_height + text_box_spacing, text_box_width,
                                       text_box_height)

    def translate(self, text):
        salt = str(random.randint(32768, 65536))
        sign = hashlib.md5((APP_ID + text + salt + APP_KEY).encode()).hexdigest()

        params = {
            'q': text,
            'from': 'zh' if self.translation_direction else 'wyw',
            'to': 'wyw' if self.translation_direction else 'zh',
            'appid': APP_ID,
            'salt': salt,
            'sign': sign
        }

        try:
            response = requests.get(BASE_URL, params=params)
            result = json.loads(response.text)
            return result['trans_result'][0]['dst']
        except Exception as e:
            print(f"翻译出错: {e}")
            return "翻译服务暂不可用"

    def draw(self):
        screen.fill(BACKGROUND_COLOR)

        # 绘制标题
        title = title_font.render("文言文翻译器", True, ACCENT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        # 绘制按钮
        for button in self.buttons:
            color = ACTIVE_COLOR if button["active"] else BUTTON_COLOR
            pygame.draw.rect(screen, color, button["rect"], border_radius=12)
            pygame.draw.rect(screen, TEXT_COLOR, button["rect"], 2, border_radius=12)
            text = button_font.render(button["text"], True, BUTTON_TEXT_COLOR)
            screen.blit(text, (button["rect"].x + button["rect"].width // 2 - text.get_width() // 2,
                               button["rect"].y + button["rect"].height // 2 - text.get_height() // 2))

        # 绘制输入框
        if self.active_input:
            pygame.draw.rect(screen, ACCENT_COLOR, self.input_rect, border_radius=12)
        else:
            pygame.draw.rect(screen, INPUT_BG_COLOR, self.input_rect, border_radius=12)
        pygame.draw.rect(screen, TEXT_COLOR, self.input_rect, 2, border_radius=12)

        # 绘制输出框
        pygame.draw.rect(screen, OUTPUT_BG_COLOR, self.output_rect, border_radius=12)
        pygame.draw.rect(screen, TEXT_COLOR, self.output_rect, 2, border_radius=12)

        # 绘制文本标签
        input_label = text_font.render("输入文本:", True, TEXT_COLOR)
        screen.blit(input_label, (self.input_rect.x + 10, self.input_rect.y - 35))

        output_label = text_font.render("翻译结果:", True, TEXT_COLOR)
        screen.blit(output_label, (self.output_rect.x + 10, self.output_rect.y - 35))

        # 渲染输入文本
        input_lines = []
        current_line = ""
        for word in self.input_text:
            test_line = current_line + word
            if text_font.size(test_line)[0] < self.input_rect.width - 20:
                current_line = test_line
            else:
                input_lines.append(current_line)
                current_line = word
        if current_line:
            input_lines.append(current_line)

        for i, line in enumerate(input_lines[-8:]):  # 最多显示8行
            text_surface = text_font.render(line, True, TEXT_COLOR)
            screen.blit(text_surface, (self.input_rect.x + 15, self.input_rect.y + 15 + i * 35))

        # 绘制光标
        if self.active_input and self.cursor_visible:
            if self.input_text:
                cursor_x = self.input_rect.x + 15 + text_font.size(self.input_text[-8:])[0]
            else:
                cursor_x = self.input_rect.x + 15  # 当输入框为空时，光标在左边界
            cursor_y = self.input_rect.y + 15 + (min(len(input_lines[-8:]), 8) - 1) * 35
            pygame.draw.line(screen, TEXT_COLOR, (cursor_x, cursor_y), (cursor_x, cursor_y + 30), 2)

        # 渲染输出文本
        output_surface = text_font.render(self.output_text, True, TEXT_COLOR)
        screen.blit(output_surface, (self.output_rect.x + 15, self.output_rect.y + 15))

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()

            # 检测按钮悬停状态
            for button in self.buttons:
                button["active"] = button["rect"].collidepoint(mouse_pos)

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # 检查方向选择按钮
                        if self.buttons[0]["rect"].collidepoint(event.pos):
                            self.translation_direction = 0
                            self.buttons[0]["active"] = True
                            self.buttons[1]["active"] = False
                        elif self.buttons[1]["rect"].collidepoint(event.pos):
                            self.translation_direction = 1
                            self.buttons[0]["active"] = False
                            self.buttons[1]["active"] = True

                        # 检查翻译按钮
                        elif self.buttons[2]["rect"].collidepoint(event.pos) and self.input_text:
                            self.output_text = self.translate(self.input_text)

                        # 检查输入框
                        self.active_input = self.input_rect.collidepoint(event.pos)
                        if self.active_input:
                            pygame.key.set_text_input_rect(self.input_rect)  # 设置输入法候选框位置

                elif event.type == KEYDOWN and self.active_input:
                    if event.key == K_RETURN:
                        if self.input_text:
                            self.output_text = self.translate(self.input_text)
                    elif event.key == K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if event.unicode:
                            self.input_text += event.unicode

                elif event.type == pygame.TEXTINPUT and self.active_input:
                    self.input_text += event.text

            # 光标闪烁逻辑
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

            self.draw()
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = TranslatorGUI()
    app.run()