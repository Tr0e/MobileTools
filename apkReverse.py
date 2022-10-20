# @Time  : 2022/10/21 1:10
# @Author: Tr0e
# @Blog  : https://tr0e.github.io/

import os
import time
from colorama import Fore, Style


def reverse():
    """
    借助jadx工具，批量反编译指定文件夹apkPath下的所有APK，输出到outputPath
    :return: null
    """
    apkPath = os.walk("D:/tmp/TestApk/")
    toolPath = "D:/Security/Mobile/jadx/jadx-1.4.4/bin/jadx"
    outputPath = "D:/tmp/JadxResult/"
    start = time.time()
    num = 1
    for path, dir_list, file_list in apkPath:
        for file_name in file_list:
            if file_name.endswith('.apk'):
                print(Fore.GREEN + "[*****************************************]" + Style.RESET_ALL)
                print("[" + str(num) + "/" + str(len(file_list)) + "]" + "正在反编译的APK：" + file_name)
                path_apk = os.path.join(path, file_name)
                command = toolPath + " -d " + outputPath + file_name + " -j 4 " + path_apk
                os.system(command)
                num = num + 1
    end = time.time()
    print(Fore.GREEN + "[*]Done." + "Totally time is " + str(end - start) + "s.Enjoy it!")


if __name__ == '__main__':
    reverse()
    exit(0)

