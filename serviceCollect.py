# @File  : serviceCollect.py
# @Time  : 2022/10/30 8:37
# @Author: Tr0e
# @Blog  : https://tr0e.github.io/

import os
import time

import pandas as pd
from colorama import Fore, init

init(autoreset=True)
serviceDict = {}  # 用于全局存放所有系统服务的字典（key:value=服务名：aidl文件名）
interfaceDict = {}  # 用于全局存放所有系统服务接口的字典（key:value=服务名：接口列表）
transactionDict = {}  # 用于全局存放所有系统服务接口的transaction Code字典的嵌套字典（key:value=服务名：接口与code值字典）


def getServiceList():
    """
    生成系统服务、AIDL文件的字典
    :return: null
    """
    global serviceDict
    print(Fore.BLUE + "[*]Start collecting data…")
    localTxtFile = "data/serviceList.txt"
    serviceListCmd = "adb shell service list >" + localTxtFile
    os.system(serviceListCmd)
    print("[+]successfully save service list to %s." % localTxtFile)
    lineNum = 1
    with open(localTxtFile, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if lineNum == 1:
                lineNum = lineNum + 1
                continue
            else:
                # 提取每行格式为：”2	nfc: [android.nfc.INfcAdapter]“的服务名”nfc"和aidl文件名
                serviceName = line.strip('\n').split(":")[0].split("\t")[1]
                aidlFileName = line.strip('\n').split(":")[1].lstrip(" ")[1:-1]
                serviceDict[serviceName] = aidlFileName
    print("[+]Len of serviceDict：" + str(len(serviceDict)))
    # print("[+]Data of serviceDict：" + str(serviceDict))
    print(Fore.BLUE + "[*]successfully collect data.")


def findAidlPath(filePath, aidlFileName):
    """
    查询指定文件夹下的aidl文件的绝对路径（支持目录嵌套）
    :param filePath: 存放了反编译资源的目标文件夹
    :param aidlFileName: aidl文件名称
    :return: 目标aidl文件的路径
    """
    for filePath, dirNames, fileNames in os.walk(filePath):
        for filename in fileNames:
            if filename == aidlFileName + ".java":
                result = os.path.join(filePath, filename)
                # print(Fore.GREEN + "[+]Path is: %s" % result)
                return result


def getAidlFile(serviceName, aidlFilePath):
    """
    从AIDL文件提取出该服务所有接口的列表
    :param serviceName: 服务名称
    :param aidlFilePath: aidl文件的路径，
    :return: 服务接口列表（含接口名、返回值、参数等）
    """
    # 路径如：r"D:\tmp\serviceFuzz\result\framework.apk\sources\android\app\IActivityManager.java"
    getTransactionDict(serviceName, aidlFilePath)  # 先生成TransactionCode字典
    with open(aidlFilePath, 'r', encoding='utf-8') as f:
        allJava = f.read()
        start = allJava.find('public static class Default implements')
        end = allJava.find('public IBinder asBinder()')
        interfaceInfo = allJava[start:end].replace("\n\n", "\n").strip("\n")
        # print(interfaceInfo)
    interfaceList = interfaceInfo.split("\n")
    # print(interfaceList)
    # 直接在原列表上使用pop删除会出现各种乱七八糟的错误，故使用新的列表来存储符合要求的原列表元素
    newInterfaceList = []
    for lineData in interfaceList:
        if "throws RemoteException" in lineData and "public" in lineData:
            lineData = lineData.lstrip(" ")
            lineData = lineData.replace("public", "").lstrip(" ")
            lineData = lineData.replace(" throws RemoteException {", "")
            newInterfaceList.append(lineData)
        else:
            continue
    # print(len(newInterfaceList))
    # print(Fore.GREEN + str(newInterfaceList))
    global interfaceDict
    interfaceDict[serviceName] = newInterfaceList
    return newInterfaceList


def getTransactionDict(serviceName, aidlFilePath):
    """
    生成所有服务的接口：Code值字典的嵌套字典transactionDict（key:value=服务名：每个服务的所有接口与其对应code值字典）
    :param serviceName: 服务名称
    :param aidlFilePath: aidl文件的路径
    :return: null
    """
    with open(aidlFilePath, 'r', encoding='utf-8') as f:
        allJava = f.read()
        start = allJava.find('static final int TRANSACTION')
        end = allJava.find('public Stub() {')
        interfaceInfo = allJava[start: end].replace("\n\n", "\n").strip("\n")
    interfaceList = interfaceInfo.split("\n")
    interfaceList.pop(len(interfaceList) - 1)
    CodeDict = {}
    for lineData in interfaceList:
        lineData = lineData.lstrip(" ")
        interfaceName = lineData.split("=")[0][29:-1]
        transactionCode = lineData.split("=")[1].replace(";", "").lstrip(" ")
        CodeDict[interfaceName] = transactionCode
    global transactionDict
    transactionDict[serviceName] = CodeDict
    # print(transactionDict)


def writeDataToXlsx(xlsxPath):
    """
    将数据转换成xlsx格式的表格
    :param xlsxPath: 输出的xlsx文件路径
    :return: null
    """
    dataSource = {}
    dictCol0List = []
    dictCol1List = []
    dictCol2List = []
    dictCol3List = []
    dictCol4List = []
    dictCol5List = []
    global interfaceDict, serviceDict, transactionDict
    # 目标行数据样例：'void addPackageDependency(String str)'
    for service, interfaces in interfaceDict.items():
        if len(interfaces) > 1:
            for interface in interfaces:
                aidlName = interface.split("(")[0].split(" ")[1]
                try:
                    dictCol0List.append(service)
                    dictCol1List.append(serviceDict[service])
                    dictCol2List.append(transactionDict[service][aidlName])
                    dictCol3List.append(aidlName)
                    dictCol4List.append(interface.split("(")[0].split(" ")[0])
                    dictCol5List.append(interface.split("(")[1][0:-1])
                except IndexError as e:
                    print(e)
                    continue
    # 设置xlsx表格每列数据的源数据列表
    dataSource["ServiceName"] = dictCol0List
    dataSource["AIDLName"] = dictCol1List
    dataSource["TransactionCode"] = dictCol2List
    dataSource["InterfaceName"] = dictCol3List
    dataSource["ReturnType"] = dictCol4List
    dataSource["ParaType"] = dictCol5List
    # print(dataSource)
    print(Fore.BLUE + "[*]Start generating xlsx…")
    writer = pd.ExcelWriter(xlsxPath)
    dataFrame = pd.DataFrame(dataSource)
    dataFrame.to_excel(writer, sheet_name="sheet1")
    writer.close()  # 保存writer中的数据至excel
    print(Fore.BLUE + "[*]Successfully generated xlsx!")


def main():
    """
    开始生成系统服务统计数据表格
    :return: 生成最终的xlsx数据文档
    """
    start = time.time()
    getServiceList()
    num = 1
    successNum = 0
    for key, value in serviceDict.items():
        if value != '' and "IDevicePolicyManager" not in value:  # Native类型的Service暂不支持获取AIDL文件
            # print(value)
            path = findAidlPath(r"D:\tmp\serviceFuzz\result", value.split(".")[-1])
            if path is not None:
                print("[%d/%d]正在分析的文件: " % (num, len(serviceDict)) + path)
                getAidlFile(key, path)
                successNum = successNum + 1
        num = num + 1
    # print(transactionDict)
    print(Fore.BLUE + "[*]总共成功分析了{0}个服务的AIDL文件!".format(successNum))
    writeDataToXlsx("data/serviceList.xlsx")
    end = time.time()
    print(Fore.GREEN + "[*]Done.Totally time is " + str(end - start) + "s.Enjoy it!")


def copyRight():
    print(Fore.GREEN + "************** CopyRight ****************")
    print(Fore.GREEN + "             Welcome to use               ")
    print(Fore.GREEN + "     Author: Tr0e                         ")
    print(Fore.GREEN + "     Github: https://github.com/Tr0e      ")
    print(Fore.GREEN + "     Blog  : https://tr0e.github.io       ")
    print(Fore.GREEN + "*****************************************")


if __name__ == '__main__':
    copyRight()
    main()
    exit(0)
