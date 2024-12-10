import sys
import time
import keyboard
import pyautogui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox,
                            QScrollArea)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

class KeyCatchLineEdit(QLineEdit):
    def __init__(self, parent=None, command_mode=False):
        super().__init__(parent)
        self.setReadOnly(True)
        self.command_mode = command_mode
        self.command_text = ""
        self.ENTER_MARKER = "{ENTER}" 
        self.is_trigger_key = False 
        
        # 기본 스타일 설정
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #B0B0B0;
                border-radius: 3px;
                padding: 4px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #0078D7;
                background-color: #F0F8FF;
            }
        """)
        
    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.command_mode:
            self.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #0078D7;
                    border-radius: 3px;
                    padding: 4px;
                    background-color: #F0F8FF;
                }
            """)
        else:
            self.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #FF4500;
                    border-radius: 3px;
                    padding: 4px;
                    background-color: #FFF0F0;
                }
            """)
            
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #B0B0B0;
                border-radius: 3px;
                padding: 4px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #0078D7;
                background-color: #F0F8FF;
            }
        """)
        
    def keyPressEvent(self, event):
        if self.command_mode:
            key = event.key()
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                self.command_text += self.ENTER_MARKER
            else:
                key_text = event.text()
                if key_text:
                    self.command_text += key_text
            self.setText(self.command_text)
            
            if isinstance(self.parent(), QWidget):
                window = self.window()
                if isinstance(window, MacroGUI):
                    window.update_macro_settings()
        else:
            key_text = event.text().upper()
            key = event.key()
            
             # 모든 키에 대해 처리
            if key in range(Qt.Key_Space, Qt.Key_AsciiTilde + 1):
                key_text = event.text().upper()
            elif key == Qt.Key_Home:
                key_text = 'HOME'
            elif key == Qt.Key_End:
                key_text = 'END'
            elif key == Qt.Key_PageUp:
                key_text = 'PAGEUP'
            elif key == Qt.Key_PageDown:
                key_text = 'PAGEDOWN'
            elif key == Qt.Key_Insert:
                key_text = 'INSERT'
            elif key == Qt.Key_Delete:
                key_text = 'DELETE'
            elif key == Qt.Key_Backspace:
                key_text = 'BACKSPACE'
            elif key == Qt.Key_Left:
                key_text = 'LEFT'
            elif key == Qt.Key_Right:
                key_text = 'RIGHT'
            elif key == Qt.Key_Up:
                key_text = 'UP'
            elif key == Qt.Key_Down:
                key_text = 'DOWN'
            elif key == Qt.Key_Escape:
                key_text = 'ESC'
            elif key == Qt.Key_Tab:
                key_text = 'TAB'
            elif key == Qt.Key_Shift:
                key_text = 'SHIFT'
            elif key == Qt.Key_Control:
                key_text = 'CTRL'
            elif key == Qt.Key_Alt:
                key_text = 'ALT'
            elif key == Qt.Key_Meta:
                key_text = 'META'
            elif key == Qt.Key_CapsLock:
                key_text = 'CAPSLOCK'
            elif key == Qt.Key_NumLock:
                key_text = 'NUMLOCK'
            elif key == Qt.Key_ScrollLock:
                key_text = 'SCROLLLOCK'
            elif key == Qt.Key_F1:
                key_text = 'F1'
            elif key == Qt.Key_F2:
                key_text = 'F2'
            elif key == Qt.Key_F3:
                key_text = 'F3'
            elif key == Qt.Key_F4:
                key_text = 'F4'
            elif key == Qt.Key_F5:
                key_text = 'F5'
            elif key == Qt.Key_F6:
                key_text = 'F6'
            elif key == Qt.Key_F7:
                key_text = 'F7'
            elif key == Qt.Key_F8:
                key_text = 'F8'
            elif key == Qt.Key_F9:
                key_text = 'F9'
            elif key == Qt.Key_F10:
                key_text = 'F10'
            elif key == Qt.Key_F11:
                key_text = 'F11'
            elif key == Qt.Key_F12:
                key_text = 'F12'
            elif key == Qt.Key_Return or key == Qt.Key_Enter:
                key_text = 'ENTER'
            
            if key_text:
                self.setText(key_text)
                if isinstance(self.parent(), QWidget):
                    window = self.window()
                    if isinstance(window, MacroGUI):
                        window.update_macro_settings()
    
    def clear_command(self):
        self.command_text = ""
        self.setText("")
        if isinstance(self.parent(), QWidget):
            window = self.window()
            if isinstance(window, MacroGUI):
                window.update_macro_settings()

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
        layout.addWidget(self.input_text)
        
        # 키 입력 딜레이
        self.key_delay = QSpinBox()
        self.key_delay.setRange(1, 1000)
        self.key_delay.setValue(100)
        self.key_delay.setFixedWidth(70)
        self.key_delay.valueChanged.connect(self.settings_changed)
        layout.addWidget(self.key_delay)
        
        # 트리거 키
        self.trigger_key = KeyCatchLineEdit()
        self.trigger_key.setPlaceholderText("트리거 키")
        self.trigger_key.setText('F6')
        self.trigger_key.setFixedWidth(100)
        self.trigger_key.textChanged.connect(self.settings_changed)
        layout.addWidget(self.trigger_key)
        
        # 초기화 버튼
        self.clear_button = QPushButton('초기화')
        self.clear_button.setFixedWidth(50)
        self.clear_button.clicked.connect(self.clear_settings)
        layout.addWidget(self.clear_button)
        
        # 삭제 버튼
        self.delete_button = QPushButton('삭제')
        self.delete_button.setFixedWidth(50)
        self.delete_button.clicked.connect(self.deleteLater)
        layout.addWidget(self.delete_button)

    def clear_settings(self):
        self.input_text.clear_command()
        self.key_delay.setValue(100)
        self.trigger_key.setText('F6')
        self.settings_changed()

    def settings_changed(self):
        if isinstance(self.window(), MacroGUI):
            self.window().update_macro_settings()

class MacroThread(QThread):
    finished = pyqtSignal()
    status_signal = pyqtSignal(str)
    
    def __init__(self, settings_list, start_key):
        super().__init__()
        self.settings_list = settings_list
        self.start_key = start_key
        self.running = True
        self.macro_enabled = False
        self.is_editing = False

    def run(self):
        self.status_signal.emit("매크로 대기 중...")
        while self.running:
            try:

                # 편집 모드일 때는 매크로 동작 중지
                if self.is_editing:
                    time.sleep(0.01)
                    continue
                # 시작/종료 키로 매크로 ON/OFF 전환
                current_start_key = self.start_key  # 현재 설정된 시작/종료 키 사용
                if keyboard.is_pressed(current_start_key):
                    time.sleep(0.2)
                    self.macro_enabled = not self.macro_enabled
                    status = "실행 중" if self.macro_enabled else "일시 중지"
                    self.status_signal.emit(f"매크로 {status}")

                # 매크로가 활성화된 상태에서만 동작
                if self.macro_enabled:
                    current_settings = self.settings_list  # 현재 설정된 매크로 목록 사용
                    for settings in current_settings:
                        if keyboard.is_pressed(settings['trigger_key']):
                            time.sleep(0.2)
                            self.status_signal.emit("커맨드 입력 중...")
                            
                            commands = settings['command']
                            if commands:
                                char_index = 0
                                while char_index < len(commands):
                                    if not self.macro_enabled:
                                        break
                                    
                                    # {ENTER} 검사
                                    if (char_index + 7 <= len(commands) and 
                                        commands[char_index:char_index + 7] == "{ENTER}"):
                                        keyboard.press_and_release('enter')
                                        char_index += 7  # {ENTER} 길이만큼 인덱스 증가
                                    else:
                                        keyboard.write(commands[char_index])
                                        char_index += 1
                                    time.sleep(settings['key_delay'] / 1000)
                                
                                self.status_signal.emit("매크로 실행 중")
                
                time.sleep(0.01)
                
            except Exception as e:
                self.status_signal.emit(f"오류 발생: {str(e)}")
                break
        
        self.finished.emit()

class MacroGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.macro_thread = None
        self.is_editing = False
        self.start_macro()
        
    def initUI(self):
        self.setWindowTitle('매크로 설정')
        self.setGeometry(300, 300, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 상태 표시 라벨
        self.status_label = QLabel('대기 중...')
        self.status_label.setFont(QFont('Arial', 12))
        self.status_label.setStyleSheet('color: blue;')
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
        header_layout.addWidget(QLabel('입력할 커맨드'))
        header_layout.addWidget(QLabel('딜레이(ms)'))
        header_layout.addWidget(QLabel('트리거 키'))
        header_layout.addWidget(QLabel(''))  # 버튼들 공간
        header_layout.addWidget(QLabel(''))  # 버튼들 공간
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
        self.start_key.setText('PAUSE')
        self.start_key.textChanged.connect(self.update_macro_settings)
        start_key_layout.addWidget(self.start_key)
        main_layout.addLayout(start_key_layout)
        
        # 도움말 추가
        help_text = """
        사용법:
        1. 각 줄에 커맨드, 딜레이, 트리거 키를 설정하세요
        2. '매크로 추가' 버튼으로 새로운 매크로를 추가할 수 있습니다
        3. 시작/종료 키(PAUSE)를 눌러 매크로를 시작/종료할 수 있습니다
        4. 매크로가 실행 중일 때 각 트리거 키를 눌러 해당 커맨드를 실행하세요
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
                    'key_delay': widget.key_delay.value(),
                    'trigger_key': widget.trigger_key.text().lower(),
                }
                settings_list.append(settings)
        return settings_list

    def start_macro(self):
        settings_list = self.get_macro_settings()
        self.macro_thread = MacroThread(settings_list, self.start_key.text().lower())
        self.macro_thread.finished.connect(self.macro_finished)
        self.macro_thread.status_signal.connect(self.update_status)
        self.macro_thread.start()
        
    def update_macro_settings(self):
        if self.macro_thread:
            self.macro_thread.settings_list = self.get_macro_settings()
            self.macro_thread.start_key = self.start_key.text().lower()
        
    def macro_finished(self):
        self.status_label.setText("매크로 종료됨")
        
    def update_status(self, message):
        self.status_label.setText(message)

    def closeEvent(self, event):
        if self.macro_thread and self.macro_thread.isRunning():
            self.macro_thread.running = False
            self.macro_thread.wait()
        event.accept()

    def focusChanged(self, old, new):
        # 포커스 변경 시 편집 모드 상태 업데이트
        if isinstance(new, KeyCatchLineEdit):
            self.is_editing = True
        else:
            self.is_editing = False
        if self.macro_thread:
            self.macro_thread.is_editing = self.is_editing

if __name__ == '__main__':
    pyautogui.FAILSAFE = True
    app = QApplication(sys.argv)
    macro_gui = MacroGUI()

    app.focusChanged.connect(macro_gui.focusChanged)
    macro_gui.show()
    sys.exit(app.exec_())