# @File  : intentAnalyze
# @Time  : 2022/11/12 10:10
# @Author: Tr0e
# @Blog  : https://tr0e.github.io/

import os
import time
import pandas as pd
from colorama import Fore, init
from xml.etree.ElementTree import parse
from func_timeout import func_set_timeout

init(autoreset=True)
componentFinallyDict = {}  # 存储最终所有APK的四大组件属性的字典，格式为：{PackageName:"{组件类型:"组件名:exported属性值"}"}
vulPermissionDict = {}  # 存储最终所有APK未定义的权限的字典，格式为：{PackageName:未定义权限列表}，PackageName=“APK名.apk/com.XXX.XXX”


def analyzeAndroidManifest(file_path):
    """
    生成指定文件夹下所有APP的四大组件属性的字典，格式为：{PackageName:"{组件类型:"组件名:exported属性值"}"}
    :param file_path: 存储反编译后的APP资源文件的路径
    :return: {PackageName:"{组件类型:"组件名:exported属性值"}"}的字典
    """
    global componentFinallyDict
    for file_ls in os.listdir(file_path):
        print(Fore.BLUE + "APPName: " + file_ls)
        path = str(file_path) + "/" + str(file_ls) + "/resources/AndroidManifest.xml"
        packageName = file_ls + "/" + getPackageName(path)  # APP的名称+包名，如“Mms.apk/com.android.mms”
        componentDict = getComponentDict(path)
        componentFinallyDict[packageName] = componentDict
    # print(str(componentFinallyDict))
    print(Fore.BLUE + "[*]Successfully analyze all AndroidManifest!")


def getPackageName(filePath):
    """
    读取AndroidManifest.xml文件中包名的属性
    :param filePath: AndroidManifest.xml文件路径
    :return: PackageName
    """
    tree = parse(filePath)
    root = tree.getroot()
    packageName = root.attrib['package']
    print(Fore.BLUE + "PackageName: " + packageName)
    return packageName


def getComponentDict(filePath):
    """
    获取指定AndroidManifest.xml文件中包含的所有四大组件的{组件类型:"组件名:exported属性值"}的字典
    :param filePath: AndroidManifest.xml文件路径
    :return: {组件类型:"组件名:exported属性值"}的字典
    """
    tree = parse(filePath)
    namespace = "{http://schemas.android.com/apk/res/android}"
    componentTypeList = {"activity", "service", "receiver", "provider"}
    componentAllDict = {}  # 存储某个App的所有组件的字典，格式：{组件类型:"组件名:eported属性值"}
    componentOneDict = {}  # 存储某个App某类组件的字典，格式：{"组件名:eported属性值"}
    for componentType in componentTypeList:
        nodelist = tree.findall('application/' + componentType)
        for node in nodelist:
            componentName = node.get(namespace + 'name')
            if node.get(namespace + 'exported') is not None:
                componentExported = node.get(namespace + 'exported')
            else:
                componentExported = "true"  # 兼容Android 12以下版本，未设置exported属性，默认True
            componentOneDict[componentName] = componentExported
        print("%s 组件的字典：" % componentType + str(componentOneDict))
        componentAllDict[componentType] = componentOneDict
        componentOneDict = {}  # 将中间字典存储到目标字典后，置空并进入下个循环收集另一类组件的数据
    # print("最终的数据：" + str(intentAllDict))
    print(Fore.GREEN + "****************************************")
    return componentAllDict


def writeDataToXlsx(xlsxPath):
    """
    将字典里面存储的Intent数据转换成xlsx格式的表格
    :param xlsxPath: 输出的xlsx文件路径
    :return: null
    """
    dataSource = {}
    dictCol0List = []
    dictCol1List = []
    dictCol2List = []
    dictCol3List = []
    dictCol4List = []
    global componentFinallyDict
    # 数据源格式为：{PackageName:"{组件类型:"组件名:exported属性值"}"}，其中PackageName=APP的名称+包名，如“Mms.apk/com.android.mms”
    for packageName, componentDict in componentFinallyDict.items():
        for componentType, componentDictExported in componentDict.items():
            for componentName, exported in componentDictExported.items():
                try:
                    dictCol0List.append(str(packageName).split("/")[0])
                    dictCol1List.append(str(packageName).split("/")[1])
                    dictCol2List.append(componentType)
                    dictCol3List.append(componentName)
                    dictCol4List.append(exported)
                except IndexError as e:
                    print(e)
                    continue
    # 设置xlsx表格每列数据的源数据列表
    dataSource["APPName"] = dictCol0List
    dataSource["PackageName"] = dictCol1List
    dataSource["ComponentType"] = dictCol2List
    dataSource["ComponentName"] = dictCol3List
    dataSource["exported"] = dictCol4List
    # print(dataSource)
    print(Fore.BLUE + "[*]Start generating xlsx…")
    writer = pd.ExcelWriter(xlsxPath)
    dataFrame = pd.DataFrame(dataSource)
    dataFrame.to_excel(writer, sheet_name="sheet1")
    writer.close()  # 保存writer中的数据至excel
    print(Fore.BLUE + "[*]Successfully generated xlsx!")


def analyzePermissions(file_path):
    """
    生成指定文件夹下所有APP的未定义组件的字典，格式为：{PackageName:未定义组件列表}
    :param file_path: 存储反编译后的APP资源文件的路径
    :return: {PackageName:未定义组件列表}的字典
    """
    global vulPermissionDict
    for file_ls in os.listdir(file_path):
        print(Fore.BLUE + "APPName: " + file_ls)
        path = str(file_path) + "/" + str(file_ls) + "/resources/AndroidManifest.xml"
        packageName = file_ls + "/" + getPackageName(path)  # APP的名称+包名，如“Mms.apk/com.android.mms”
        permissionList = getPermissionErrorList(path)
        vulPermissionDict[packageName] = permissionList
    # print(str(vulPermissionDict))
    print(Fore.BLUE + "[*]Successfully analyze all Permissions!")


def getPermissionErrorList(filePath):
    """
    读取AndroidManifest.xml文件中的未定义权限列表
    :param filePath: AndroidManifest.xml文件路径
    :return 某个APP的未定义权限列表
    """
    tree = parse(filePath)
    root = tree.getroot()
    namespace = "{http://schemas.android.com/apk/res/android}"
    # packageName = root.attrib['package']
    # print(Fore.BLUE + "PackageName: " + packageName)
    usesPermissionList = []
    undefinePermissionList = []
    for child in root.iter('uses-permission'):
        permissionName = child.get(namespace + 'name')
        usesPermissionList.append(permissionName)
        # print(permissionName)
        cmd = "adb shell pm list permissions | findstr " + permissionName
        if execCommand(cmd) == "":
            # if permissionName.startswith("android.permission"):
            #     continue
            undefinePermissionList.append(permissionName)
    print(undefinePermissionList)
    print(Fore.GREEN + "****************************************")
    return undefinePermissionList


@func_set_timeout(3)
def execCommand(command):
    return os.popen(command).read().strip('\n')


def writePermissionXlsx(xlsxPath):
    """
    将字典里面存储的未定义权限数据转换成xlsx格式的表格
    :param xlsxPath: 输出的xlsx文件路径
    :return: null
    """
    dataSource = {}
    dictCol1List = []
    dictCol2List = []
    dictCol3List = []
    global vulPermissionDict
    # 数据源格式为：{PackageName:未定义权限列表}，其中PackageName=APP的名称+包名，如“Mms.apk/com.android.mms”
    for packageName, permissionList in vulPermissionDict.items():
        for vulPermission in permissionList:
            try:
                dictCol1List.append(str(packageName).split("/")[0])
                dictCol2List.append(str(packageName).split("/")[1])
                dictCol3List.append(vulPermission)
            except IndexError as e:
                print(e)
                continue
    # 设置xlsx表格每列数据的源数据列表
    dataSource["APPName"] = dictCol1List
    dataSource["PackageName"] = dictCol2List
    dataSource["PermissionName"] = dictCol3List
    # print(dataSource)
    print(Fore.BLUE + "[*]Start generating xlsx…")
    writer = pd.ExcelWriter(xlsxPath)
    dataFrame = pd.DataFrame(dataSource)
    dataFrame.to_excel(writer, sheet_name="sheet1")
    writer.close()  # 保存writer中的数据至excel
    print(Fore.BLUE + "[*]Successfully generated xlsx!")


def copyRight():
    print(Fore.GREEN + "************** CopyRight ****************")
    print(Fore.GREEN + "             Welcome to use               ")
    print(Fore.GREEN + "     Author: Tr0e                         ")
    print(Fore.GREEN + "     Github: https://github.com/Tr0e      ")
    print(Fore.GREEN + "     Blog  : https://tr0e.github.io       ")
    print(Fore.GREEN + "*****************************************")


if __name__ == '__main__':
    copyRight()
    start = time.time()
    # 对批量APP四大组件的exported属性进行收集并生成统计表格
    analyzeAndroidManifest("D:/tmp/Result")
    writeDataToXlsx("data/result/intent.xlsx")
    # 对批量APP排查未定义权限并生成统计表格
    # analyzePermissions("D:/tmp/Result")
    # writePermissionXlsx("data/result/permission.xlsx")
    end = time.time()
    print(Fore.BLUE + "[*]Done.Totally time is " + str(end - start) + "s.Enjoy it!")
    exit(0)
