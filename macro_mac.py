import sys
import time
import random
from pynput import keyboard as kb
from pynput.keyboard import Key, Controller
import pyautogui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox,
                            QScrollArea, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# 맥용 키 매핑
MAC_KEY_MAPPING = {
    'PAUSE': Key.f12,
    'F1': Key.f1,
    'F2': Key.f2,
    'F3': Key.f3,
    'F4': Key.f4,
    'F5': Key.f5,
    'F6': Key.f6,
    'F7': Key.f7,
    'F8': Key.f8,
    'F9': Key.f9,
    'F10': Key.f10,
    'F11': Key.f11,
    'F12': Key.f12,
    'ENTER': Key.enter,
    'SPACE': Key.space,
    'TAB': Key.tab,
    'SHIFT': Key.shift,
    'CTRL': Key.ctrl,
    'ALT': Key.alt,
    'OPTION': Key.alt,
    'COMMAND': Key.cmd,
    'ESC': Key.esc
}

class KeyCatchLineEdit(QLineEdit):
    def __init__(self, parent=None, command_mode=False):
        super().__init__(parent)
        self.command_mode = command_mode
        self.command_text = ""
        self.apply_style()
        
    def apply_style(self):
        self.setStyleSheet("""
            QLineEdit {3
                border: 1px solid #B0B0B0;
                border-radius: 3px;
                padding: 4px;
                background-color: #F5F5F5;
                color: black !important;
            }
        """)
        
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.apply_style()
            
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.apply_style()
        
    def keyPressEvent(self, event):
        if self.command_mode:
            key = event.key()
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                self.command_text += "nt"
            else:
                key_text = event.text()
                if key_text:
                    self.command_text += key_text
            self.setText(self.command_text)
        else:
            key_text = event.text().upper()
            key = event.key()
            
            # 맥용 키 매핑
            if key == Qt.Key_F1: key_text = 'F1'
            elif key == Qt.Key_F2: key_text = 'F2'
            elif key == Qt.Key_F3: key_text = 'F3'
            elif key == Qt.Key_F4: key_text = 'F4'
            elif key == Qt.Key_F5: key_text = 'F5'
            elif key == Qt.Key_F6: key_text = 'F6'
            elif key == Qt.Key_F7: key_text = 'F7'
            elif key == Qt.Key_F8: key_text = 'F8'
            elif key == Qt.Key_F9: key_text = 'F9'
            elif key == Qt.Key_F10: key_text = 'F10'
            elif key == Qt.Key_F11: key_text = 'F11'
            elif key == Qt.Key_F12: key_text = 'F12'
            elif key == Qt.Key_Return or key == Qt.Key_Enter: key_text = 'ENTER'
            elif key == Qt.Key_Space: key_text = 'SPACE'
            elif key == Qt.Key_Tab: key_text = 'TAB'
            elif key == Qt.Key_Shift: key_text = 'SHIFT'
            elif key == Qt.Key_Control: key_text = 'CTRL'
            elif key == Qt.Key_Alt: key_text = 'OPTION'
            elif key == Qt.Key_Meta: key_text = 'COMMAND'
            elif key == Qt.Key_Escape: key_text = 'ESC'
            
            if key_text:
                self.setText(key_text)
                
        self.apply_style()  # 키 입력 후 스타일 적용
        
        if isinstance(self.parent(), QWidget):
            window = self.window()
            if isinstance(window, MacroGUI):
                if not self.command_mode:
                    QThread.msleep(100)
                window.update_macro_settings()
    
    def clear_command(self):
        self.command_text = ""
        self.setText("")
        if isinstance(self.parent(), QWidget):
            window = self.window()
            if isinstance(window, MacroGUI):
                window.update_macro_settings()

class MacroThread(QThread):
    finished = pyqtSignal()
    status_signal = pyqtSignal(str)
    
    def __init__(self, settings_list, start_key):
        super().__init__()
        self.keyboard = Controller()
        self.settings_list = settings_list
        self.start_key = start_key
        self.running = True
        self.macro_enabled = False
        self.last_trigger_time = {}
        self.is_editing = False
        self.current_keys = set()  # 현재 눌린 키들을 추적

    def on_press(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        
        # 디버깅을 위한 출력 추가
        print(f"Pressed key: {key_char}")
        print(f"Start key: {self.start_key.upper()}")
        print(f"Current macro status: {'Enabled' if self.macro_enabled else 'Disabled'}")
        
        self.current_keys.add(key_char)
        
        if not self.is_editing:
            # 시작/종료 키 체크
            if str(key) == str(MAC_KEY_MAPPING.get(self.start_key.upper())):
                print("Start/Stop key pressed!")
                time.sleep(0.2)
                self.macro_enabled = not self.macro_enabled
                status = "🟢 매크로 실행 중" if self.macro_enabled else "🔴 매크로 일시 중지"
                self.status_signal.emit(status)
            
            # 매크로 실행
            if self.macro_enabled:
                current_time = time.time()
                for settings in self.settings_list:
                    trigger_key = settings['trigger_key'].upper()
                    print(f"Checking trigger key: {trigger_key}")  # 디버깅용
                    print(f"Current key: {str(key)}")  # 디버깅용
                    print(f"Mapped key: {str(MAC_KEY_MAPPING.get(trigger_key))}")  # 디버깅용
                    
                    if str(key) == str(MAC_KEY_MAPPING.get(trigger_key)):
                        if (trigger_key not in self.last_trigger_time or 
                            current_time - self.last_trigger_time.get(trigger_key, 0) > 0.5):
                            
                            self.last_trigger_time[trigger_key] = current_time
                            self.execute_macro(settings)

    def on_release(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        
        self.current_keys.discard(key_char)
        
        if not self.running:
            return False

    def execute_macro(self, settings):
        self.status_signal.emit("커맨드 입력 중...")
        commands = settings['command']
        if commands:
            print("\n=== 매크로 실행 정보 ===")
            print(f"입력할 커맨드: {commands}")
            print(f"최소 딜레이: {settings['min_key_delay']}ms")
            print(f"최대 딜레이: {settings['max_key_delay']}ms")
            
            char_index = 0
            while char_index < len(commands):
                if not self.macro_enabled:
                    break
                
                char = commands[char_index]
                if char.lower() == 'n' and char_index + 1 < len(commands) and commands[char_index + 1].lower() == 't':
                    print(f"Enter 키 입력")
                    self.keyboard.press(Key.enter)
                    self.keyboard.release(Key.enter)
                    char_index += 2
                else:
                    print(f"문자 입력: {char}")
                    self.keyboard.type(char)
                    char_index += 1
                    
                # 랜덤 딜레이 적용
                random_delay = random.uniform(settings['min_key_delay'], settings['max_key_delay']) / 1000
                print(f"현재 딜레이: {random_delay*1000:.2f}ms")
                time.sleep(random_delay)
            
            print("=== 매크로 실행 완료 ===\n")
            self.status_signal.emit("매크로 실행 중")

    def run(self):
        self.status_signal.emit("매크로 대기 중...")
        with kb.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            while self.running:
                time.sleep(0.01)
                if not self.running:
                    listener.stop()
                    break
            listener.join()
        
        self.finished.emit()

    def stop(self):
        self.running = False
        self.macro_enabled = False

class MacroSettingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 커맨드 입력
        self.input_text = KeyCatchLineEdit(command_mode=True)
        self.input_text.setPlaceholderText("커맨드 입력")
        self.input_text.setFixedWidth(200)  # 너비 고정
        layout.addWidget(self.input_text)
        
        # 키 입력 딜레이 (최소값)
        self.min_key_delay = QSpinBox()
        self.min_key_delay.setRange(1, 1000)
        self.min_key_delay.setValue(50)
        self.min_key_delay.setFixedWidth(70)
        self.min_key_delay.valueChanged.connect(self.settings_changed)
        layout.addWidget(self.min_key_delay)
        
        # 키 입력 딜레이 (최대값)
        self.max_key_delay = QSpinBox()
        self.max_key_delay.setRange(1, 1000)
        self.max_key_delay.setValue(90)
        self.max_key_delay.setFixedWidth(70)
        self.max_key_delay.valueChanged.connect(self.settings_changed)
        layout.addWidget(self.max_key_delay)
        
        # 트리거 키
        self.trigger_key = KeyCatchLineEdit()
        self.trigger_key.setPlaceholderText("트리거 키")
        self.trigger_key.setText('F6')
        self.trigger_key.setFixedWidth(100)
        self.trigger_key.textChanged.connect(self.settings_changed)
        layout.addWidget(self.trigger_key)
        
        # 초기화 버튼
        self.clear_button = QPushButton('3')
        self.clear_button.setFixedWidth(50)
        self.clear_button.clicked.connect(self.clear_settings)
        layout.addWidget(self.clear_button)
        
        # 삭제 버튼
        self.delete_button = QPushButton('삭제')
        self.delete_button.setFixedWidth(50)
        self.delete_button.clicked.connect(self.deleteLater)
        layout.addWidget(self.delete_button)
        
        # 남은 공간을 채움
        layout.addStretch()

    def clear_settings(self):
        self.input_text.clear_command()
        self.min_key_delay.setValue(50)
        self.max_key_delay.setValue(90)
        self.trigger_key.setText('F6')
        self.settings_changed()

    def settings_changed(self):
        if isinstance(self.window(), MacroGUI):
            self.window().update_macro_settings()

class MacroGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.check_accessibility()
        self.initUI()
        self.macro_thread = None
        self.is_editing = False
        self.start_macro()
        
    def check_accessibility(self):
        # 맥OS 접근성 권한 확인
        try:
            with kb.Events() as events:
                event = events.get(timeout=0.1)
        except:
            QMessageBox.warning(self, '접근성 권한 필요', 
                              '매크로 실행을 위해 접근성 권한이 필요합니다.\n'
                              '시스템 환경설정 > 보안 및 개인 정보 보호 > 개인 정보 보호 > '
                              '손쉬운 사용에서 이 앱을 허용해주세요.')
        
    def initUI(self):
        self.setWindowTitle('매크로 설정 (Mac)')
        self.setGeometry(300, 300, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 상태 표시 라벨
        self.status_label = QLabel('대기 중...')
        self.status_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #1a73e8;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # 매크로 설정 컨테이너
        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.settings_layout.setSpacing(10)
        
        # 스크롤 영역 설정
        scroll = QScrollArea()
        scroll.setWidget(self.settings_container)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # 컬럼 헤더
        header_layout = QHBoxLayout()
        
        # 입력할 커맨드 라벨
        command_label = QLabel('입력할 커맨드')
        command_label.setFixedWidth(200)
        command_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(command_label)
        
        # 딜레이 라벨을 수직 레이아웃으로 변경
        delay_container = QWidget()
        delay_layout = QVBoxLayout(delay_container)
        delay_layout.setContentsMargins(0, 0, 0, 0)
        delay_layout.setSpacing(2)  # 라벨 간격 조정
        
        delay_label = QLabel('딜레이(ms)')
        delay_label.setAlignment(Qt.AlignCenter)
        delay_layout.addWidget(delay_label)
        
        delay_sublabel = QLabel('최소     최대')
        delay_sublabel.setAlignment(Qt.AlignCenter)
        delay_layout.addWidget(delay_sublabel)
        
        delay_container.setFixedWidth(140)
        header_layout.addWidget(delay_container)
        
        # 트리거 키 라벨
        trigger_label = QLabel('트리거 키')
        trigger_label.setFixedWidth(100)
        trigger_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(trigger_label)
        
        # 버튼들을 위한 여백
        header_layout.addStretch()
        
        self.settings_layout.addLayout(header_layout)
        
        # 첫 번째 매크로 설정 추가
        self.add_macro_setting()
        
        # 매크로 추가 버튼
        add_button = QPushButton('매크로 추가')
        add_button.clicked.connect(self.add_macro_setting)
        main_layout.addWidget(add_button)
        
        # 시작/종료 키 설정
        start_key_layout = QHBoxLayout()
        start_key_layout.addWidget(QLabel('시작/종료 키:'))
        self.start_key = KeyCatchLineEdit()
        self.start_key.setPlaceholderText("클릭 후 키를 누르세요")
        self.start_key.setText('F12')
        self.start_key.textChanged.connect(self.update_macro_settings)
        start_key_layout.addWidget(self.start_key)
        main_layout.addLayout(start_key_layout)
        
        # 도움말 추가
        help_text = """
        사용:
        1. 각 줄에 커맨드, 딜레이, 트리거 키를 설정하세요
        2. '매크로 추가' 버튼으로 새로운 매크로를 추가할 수 있습니다
        3. 시작/종료 키(F12)를 눌러 매크로를 시작/종료할 수 있습니다
        4. 매크로가 실행 중일 때 각 트리거 키를 눌러 해당 커맨드를 실행하세요
        
        * 주의: 맥OS에서는 접근성 권한이 필요합니다
        """
        help_label = QLabel(help_text)
        help_label.setStyleSheet('color: gray;')
        main_layout.addWidget(help_label)

    def add_macro_setting(self):
        setting_widget = MacroSettingWidget()
        setting_widget.delete_button.clicked.connect(self.update_macro_settings)
        self.settings_layout.addWidget(setting_widget)
        
    def get_macro_settings(self):
        settings_list = []
        for i in range(self.settings_layout.count()):
            widget = self.settings_layout.itemAt(i).widget()
            if isinstance(widget, MacroSettingWidget):
                settings = {
                    'command': widget.input_text.command_text,
                    'min_key_delay': widget.min_key_delay.value(),
                    'max_key_delay': widget.max_key_delay.value(),
                    'trigger_key': widget.trigger_key.text(),
                }
                settings_list.append(settings)
        return settings_list
    def start_macro(self):
        settings_list = self.get_macro_settings()
        self.macro_thread = MacroThread(settings_list, self.start_key.text())
        self.macro_thread.finished.connect(self.macro_finished)
        self.macro_thread.status_signal.connect(self.update_status)
        self.macro_thread.start()
        
    def update_macro_settings(self):
        if self.macro_thread:
            self.macro_thread.settings_list = self.get_macro_settings()
            self.macro_thread.start_key = self.start_key.text()
        
    def macro_finished(self):
        self.status_label.setText("매크로 종료됨")
        
    def update_status(self, message):
        self.status_label.setText(message)

    def closeEvent(self, event):
        if self.macro_thread:
            self.macro_thread.stop()
            self.macro_thread.wait()
        event.accept()

if __name__ == '__main__':
    pyautogui.FAILSAFE = True
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    macro_gui = MacroGUI()
    
    macro_gui.show()
    sys.exit(app.exec_())