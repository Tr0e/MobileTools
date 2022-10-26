# @File  : apkReverse.py
# @Time  : 2022/10/21 01:10
# @Author: Tr0e
# @Blog  : https://tr0e.github.io/

import os
import time
import func_timeout
from colorama import Fore, init
from func_timeout import func_set_timeout

init(autoreset=True)  # 配置colorama颜色自动重置，否则得手动设置Style.RESET_ALL
apk_list = []  # 递归查询指定文件夹后获得的所有apk文件的路径列表


def pullAPK_by_SystemPath():
    """
    根据手机的app path路径，批量拉取手机中的APK文件到本地路径
    :return: null
    """
    pathList = ["system/priv-app", "system/app", "hw_product/app"]  # 执行"adb shell find . -iname *.apk 2>/dev/null"来判断路径
    print(Fore.BLUE + "[*]Start pull apk…")
    start = time.time()
    for path in pathList:
        pullCmd = "adb pull " + path + " D:/tmp/Android/TestApk/" + path.replace("/", "_")
        os.system(pullCmd)
        print(Fore.GREEN + "[+]Success pull: " + path)
    end = time.time()
    print(Fore.BLUE + "[*]Done.Totally time is " + str(end - start) + "s.Enjoy it!")


def pullAPK_by_PackageList():
    """
    根据指定的包名列表，批量拉取手机中的APK文件到本地路径
    :return: null
    """
    pkgList = []
    print(Fore.BLUE + "[*]Start pull apk…")
    with open('packageList.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            packageName = line.strip('\n')  # 去除文本中的换行符
            pkgList.append(packageName)
            try:
                pathCmd = "adb shell pm path " + packageName
                result = os.popen(pathCmd).read().strip('\n')  # 去除末尾的换行符，"package:/system/priv-app/aaa.apk"
                pkgPath = result.split(":")[1]  # 截取返回结果中的路径，去除头部多余的"package:"
                pullCmd = "adb pull " + pkgPath + " D:/tmp/Android/TestApk/" + packageName + ".apk"
                os.system(pullCmd)
                print(Fore.GREEN + "[+]Success pull: " + packageName)
            except Exception as e:
                print(Fore.RED + "[-]%s" % e)
                print(Fore.RED + "[-]Pull {0} fail, please check packageName.".format(packageName))
    print(Fore.BLUE + "[*]Done.Enjoy it!")


def apkReverse():
    """
    借助jadx工具，批量反编译指定文件夹下的所有APK（支持文件夹嵌套），输出到outputPath
    :return: null
    """
    apkPath = os.walk("D:/tmp/Android/TestApk/")
    toolPath = "D:/Security/Mobile/jadx/jadx-1.4.4/bin/jadx"
    outputPath = "D:/tmp/Android/Result/"
    find_apk("D:/tmp/Android/TestApk")
    apkTotalNum = len(apk_list)
    num = 1
    start = time.time()
    print(Fore.BLUE + "[*]Start reverse apk…")
    for path, dir_list, file_list in apkPath:  # 反编译apkPath文件夹下所有的apk文件
        for file_name in file_list:
            if file_name.endswith('.apk'):
                print(Fore.GREEN + "*****************************************")
                print("[" + str(num) + "/" + str(apkTotalNum) + "]" + "正在反编译的APK：" + file_name)
                path_apk = os.path.join(path, file_name)
                command = toolPath + " -d " + outputPath + file_name + " -j 4 " + path_apk
                try:
                    execCommand(command)
                except func_timeout.exceptions.FunctionTimedOut as e:
                    print(Fore.RED + "[-]执行超时: %s" % e)
                num = num + 1
    end = time.time()
    print(Fore.GREEN + "[*]Done.Totally time is " + str(end - start) + "s.Enjoy it!")


@func_set_timeout(180)
def execCommand(command):
    os.system(command)
    

def find_apk(file_path):
    """
    递归查询file_path文件夹下的apk文件
    :param file_path: 目标文件夹，如D:/tmp/Android，请留意最后不要加"/"
    :return: 目标文件夹下所有apk文件的列表
    """
    if os.path.isfile(file_path):
        if str(file_path).endswith(".apk"):
            apk_list.append(file_path)
    else:
        for file_ls in os.listdir(file_path):
            find_apk(str(file_path) + "/" + str(file_ls))


def copyRight():
    print(Fore.YELLOW + "************** CopyRight ****************")
    print(Fore.GREEN + "             Welcome to use               ")
    print(Fore.GREEN + "     Author: Tr0e                         ")
    print(Fore.GREEN + "     Github: https://github.com/Tr0e      ")
    print(Fore.GREEN + "     Blog  : https://tr0e.github.io       ")
    print(Fore.YELLOW + "*****************************************")


if __name__ == '__main__':
    copyRight()
    apkReverse()
    # pullAPK_by_PackageList()
    # pullAPK_by_SystemPath()
    exit(0)
