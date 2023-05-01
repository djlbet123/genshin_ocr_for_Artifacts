# 原神自动记录圣遗物词条
## 简介
    以学习为目的开发此项目，无盈利目的。
    由于原神的圣遗物强化存在随机性，许多用户寻找强化的规律。在这个项目中，使用PPOCRV3自动检测圣遗物的词条和强化结果，
    并自动录入数据，减少人力劳动。减少打标签的错误操作，避免污染数据，为后续的分析提供帮助。
[视频演示](https://www.bilibili.com/video/BV14T411h7Jw/)

## 操作说明
    原理是截取屏幕中的词条区域，进行识别，所以一定要全屏运行原神。只在4K分辨率测试过(3840*2160)测试过，
    按理说只要16:9全屏显示原神就可以，不排除有BUG，DEBUG可以自行修改main.py下第38行，改为True，
    再次运行就会保存截图的区域。有误自行修改。你也可以自定义词条的记录方式。支持对游戏和视频识别，位置对即可

## 打包好的文件
    见Release，解压好以后
    右键管理员运行启动程序.exe
    第一次运行需要安装，需要较长时间
    
## 安装环境(conda)
    conda create -n artifacts python=3.8
    conda activate artifacts
    pip install -r requirements.txt
    python main.py

## 使用
    #有两种模式，鼠标检测模式和键盘操作模式，一般在自己电脑上使用鼠标检测模式，例如
    python main.py --opt mouse
    #鼠标模式下，按下鼠标中键，程序会结束。强化过程，按鼠标左键点击就好了，会自动根据点击的区域进行相应的操作，
    #按ESC退出就不会识别了。
    #键盘模式下，'['键是识别已有圣遗物词条，']'键是识别强化结果，'\'是结束程序
    #注意！只有五星圣遗物支持多次强化同一词条的解析，例如：5星的圣遗物从0级升级到8级，生命值从0升级到448，
    #会解析出中239一次，209一次，具体实现看代码。如果不是强化在同一条词条上，5，4，3星的圣遗物都能正确记录。
    #会优先记录新出的词条，然后再从上到下的顺序记录剩下的词条

## Tested on
    Windows11
    I7-12700H
    4K分辨率(3840*2160)

## 案例
![image](https://github.com/djlbet123/genshin_ocr_for_Artifacts/blob/master/img/img0.jpg)
![image](https://github.com/djlbet123/genshin_ocr_for_Artifacts/blob/master/img/visualized_result0.jpg)
![image](https://github.com/djlbet123/genshin_ocr_for_Artifacts/blob/master/img/img1.jpg)
![image](https://github.com/djlbet123/genshin_ocr_for_Artifacts/blob/master/img/visualized_result1.jpg)

## 使用的仓库
[FastDeploy](https://github.com/PaddlePaddle/FastDeploy)
[D3DSHOT](https://github.com/SerpentAI/D3DShot)