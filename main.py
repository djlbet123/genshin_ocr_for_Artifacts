# coding:utf-8
import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QLabel
import os
import d3dshot
import time
import pynput
from pynput import mouse, keyboard
import cv2
from infer import ppocr_v3, args
import fastdeploy as fd
import os
from label import get_index, get_bias, append_func
import json
import datetime 

opt_type = args.opt
assert opt_type in ['mouse', 'board']

app = None

dir = os.path.dirname(os.path.abspath(__file__))
begin_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
if not os.path.exists(os.path.join(dir, "data")):
    os.makedirs(os.path.exists(os.path.join(dir, "data")))
file_name = os.path.join(dir, "data", f"{begin_time}.json")
data = []
citiao_mem = [] # 第一条为主词条，所有元素伤害统一记为元素伤害

shot = d3dshot.create(capture_output="numpy")
h, w, _ = shot.screenshot().shape
print(datetime.datetime.now(),": resolution is [", w, h, "]")
region = [int(w * 2440 / 3840), int(h * 426 / 2160), int(w * 3700 / 3840), int(h * 1057 / 2160)]                # 已有词条区域
strengthen = [int(w * 3156/ 3840), int(h * 1976 / 2160), int(w * 3750/ 3840), int(h * 2102 / 2160)]             # 强化按键区域
confirm = [int(w * 1573/ 3840), int(h * 1591 / 2160), int(w * 2254/ 3840), int(h * 1725 / 2160)]                # 确定按键区域
upgrade = [int(w * 955/ 3840), int(h * 1151 / 2160), int(w * 2899/ 3840), int(h * 1574 / 2160)]                 # 强化出来的词条区域
save_img = False                                                                                                # 是否保存图像，用于DEBUG，确定区域是否正确
flag, task, src, lock = 0, 0, None, None
second_per_frame = 0.05
first_text = ""
second_text = ""

def is_contains_chinese(s):
    for char in s:
        if '\u4e00' <= char <= '\u9fa5':
            return True
    return False

def NumIn(s):
    for char in s:
        if char.isdigit():
            return True
    return False

def is_contain_char(s):
    chars = ['以', '下', '及', '系', '材', '料', '原', '均'] # 误识别的字
    for char in s:
        if char in chars:
            return True
    return True if s.__contains__("生") and not s.__contains__("生命") else False

def get_lock():
    global lock
    while lock:
        time.sleep(second_per_frame)
    lock = True
    
def release_lock():
    global lock
    lock = False

def sort(result, is_strengthen = False):
    box_tmp, text_tmp = [], []
    region_tmp = strengthen if is_strengthen else region
    print(result.text)
    for i in range(len(result.boxes)):
        rel_x = result.boxes[i][0]
        if result.text[i].__contains__("+"):
            print(datetime.datetime.now(),": 不在强化界面")
            return False
        elif result.text[i] == '':
            continue
        elif not is_strengthen and result.text[i].__contains__("追加属性"):
            continue
        elif not is_strengthen and rel_x >= (region_tmp[2] - region_tmp[0]) / 4 and rel_x <= (region_tmp[2] - region_tmp[0]) / 4 * 3:
            continue
        elif is_strengthen and is_contain_char(result.text[i]):
            continue
        else:
            box_tmp.append(result.boxes[i])
            text_tmp.append(result.text[i])
            # if rel_x < (region_tmp[2] - region_tmp[0]) / 4:
            #     box_tmp[-1][0] = 0
            # elif rel_x > (region_tmp[2] - region_tmp[0]) / 4 * 3:
            #     box_tmp[-1][0] = region_tmp[2] - 1
    sorted_list = sorted(zip(box_tmp, text_tmp), key = lambda x:(x[0][1],x[0][0]))
    result.text = [i[1] for i in sorted_list]
    text_tmp = []
    if not is_strengthen:
        for i in range(0, len(result.text), 2):
            if is_contains_chinese(result.text[i+1]) and NumIn(result.text[i]):
                text_tmp.append(result.text[i+1])
                text_tmp.append(result.text[i])
            else:
                text_tmp.append(result.text[i])
                text_tmp.append(result.text[i+1])
    else:
        new_citiao, i = 0, 0
        while i < len(result.text):
            increment = 3 if i+2 < len(result.text) and abs(sorted_list[i][0][1] - sorted_list[i][0][1]) < (strengthen[3] - strengthen[1]) / 6 else 2
            new_citiao = new_citiao + 1 if increment == 2 else new_citiao
            for j in range(i, i+increment):
                if is_contains_chinese(result.text[j]):
                    text_tmp.append(result.text[j])
                    break
            for j in range(i, i+increment):
                if NumIn(result.text[j]):
                    text_tmp.append(result.text[j])
            i += increment
        for i in range(new_citiao): # 交换顺序
            text_tmp.insert(0,text_tmp[-2])
            text_tmp.insert(1,text_tmp[-1])
            text_tmp.pop()
            text_tmp.pop()
            
    result.text = text_tmp
    print(result.text)
    return True
    
def infer():
    get_lock()
    result = ppocr_v3.predict(src)
    if save_img:
        vis_im = fd.vision.vis_ppocr(src, result)
    release_lock()
    if save_img:
        cv2.imwrite("visualized_result.jpg", vis_im)
    return result

def capture(region):
    global src
    get_lock()
    src = shot.screenshot(region = region)
    src = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    if save_img:
        cv2.imwrite("img.jpg", src)
    release_lock()
    

def parsing():
    global citiao_mem, flag, src, first_text
    result = infer()
    try:
        flag = 1
        if sort(result):
            output = result.text
            first_text = "\n".join(output)
            if len(output) != 0 and output[0] != "":
                detect = []
                for i in range(0,len(output),2):
                    main, _ = get_index(output[i], output[i+1])
                    detect.append(main)
                citiao_mem = detect
                print(datetime.datetime.now(), ": ", citiao_mem)
    except Exception as e:
        print(e)
        #flag = 0

def record():
    global citiao_mem, flag, data, src, second_text
    result = infer()
    flag = 0
    # 记录变化的词条
    try:
        if sort(result, True):
            output = result.text
            second_text_tmp = []
            if citiao_mem is not None and len(citiao_mem) != 0:
                i = 0
                while i < len(output):
                    main_index, _ = get_index(output[i], output[i+1])
                    if main_index not in citiao_mem: # 新词条
                        print("出新词条",output[i], output[i+1])
                        stren_result = get_index(output[i], output[i+1], data, citiao_mem, second_text_tmp)
                        append_func(data, citiao_mem, stren_result, second_text_tmp)
                        citiao_mem.append(main_index)                        # 新出的词条加进去
                        i+=2
                    else:
                        print("词条升级",output[i], output[i+1], output[i+2])
                        bias = get_bias(main_index, output[i+1], output[i+2])
                        stren_result = get_index(output[i], bias, data, citiao_mem, second_text_tmp)
                        append_func(data, citiao_mem, stren_result, second_text_tmp)
                        i+=3
                
                second_text = "\n".join(second_text_tmp)
    except Exception as e:
        print(e)
        flag = 0

def on_click(x, y, button, pressed):
    global task, flag
    if button == pynput.mouse.Button.middle and pressed == True:
        task = -1
    if task == 0 and x > strengthen[0] and x < strengthen[2] and y > strengthen[1] and y < strengthen[3]: # 升级区域检测
        capture(region=region)
        print(datetime.datetime.now(), " : 点击了升级区域")
        task = 1
    elif task == 0 and flag == 1 and  x > confirm[0] and x < confirm[2] and y > confirm[1] and y < confirm[3]: # 确认区域检测
        capture(region=upgrade)        
        print(datetime.datetime.now(), ": 点击了确认区域")
        task = 2

def listen_mouse_nblock():
    listener = mouse.Listener(
        on_click=on_click,
    )
    listener.start()

def board_on_press(key):
    global task, flag
    """定义按下时候的响应，参数传入key"""
    try:
        if key.char == '[':
            capture(region=region)
            print(datetime.datetime.now(), " : 点击了升级区域")
            task = 1
        elif key.char == ']':
            capture(region=upgrade)        
            print(datetime.datetime.now(), ": 点击了确认区域")
            task = 2
        elif key.char == '\\':
            task = -1
    except AttributeError:
        pass

def save_data():
    if data != []:
        with open(file_name,'w') as file_object:
            json.dump(data,file_object)
        print(datetime.datetime.now(), ": saving to ", file_name)
    else:
        print("no data, won't create new file")

def listen_key_nblock():
    listener = keyboard.Listener(
        on_press=board_on_press
    )
    listener.start()  # 启动线程

class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QVBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

class main_ui(QWidget):
    def __init__(self, second_per_frame):
        super().__init__()
        self.setWindowTitle(f"{opt_type}模式")
        self.ori_widget = Widget("原有词条检测区域", self)
        self.upgrade_widget = Widget("升级词条检测区域", self)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout.addWidget(self.ori_widget)
        self.verticalLayout.addWidget(self.upgrade_widget)
        self.timer = QTimer()
        self.timer.start(second_per_frame * 1000)
        self.timer.timeout.connect(self.main_thread) 
        self.setStyleSheet('Demo{background:white}')
        self.resize(400, 400)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowOpacity(0.5)

    def main_thread(self):
        global app, task, second_text
        if task == -1:
            self.timer.stop()
            save_data()
            app.exit()
            exit()
        elif task == 1:
            parsing()
            task = 0
            second_text = ""
        elif task == 2:
            record()
            task = 0
        self.ori_widget.label.setText(first_text)
        self.upgrade_widget.label.setText(second_text)


    def mousePressEvent(self, event):        #鼠标左键按下时获取鼠标坐标
        if event.button() == Qt.LeftButton:
            self._move_drag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()
    
    def mouseMoveEvent(self, QMouseEvent):    #鼠标在按下左键的情况下移动时,根据坐标移动界面
        if Qt.LeftButton and self._move_drag:
            self.move(QMouseEvent.globalPos() - self.m_Position)
            QMouseEvent.accept()
    
    def mouseReleaseEvent(self, QMouseEvent):    #鼠标按键释放时,取消移动
        self._move_drag = False        

if __name__ == "__main__":
    try:
        if opt_type == "board":
            listen_key_nblock()
        else:
            listen_mouse_nblock()
        app = QApplication(sys.argv)
        w = main_ui(second_per_frame)
        w.show()
        app.exec()
    except Exception as e:
        print(e)
    finally:
        save_data()