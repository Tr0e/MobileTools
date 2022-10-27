# @File  : dataAnalyze.py
# @Time  : 2022/10/25 01:40
# @Author: Tr0e
# @Blog  : https://tr0e.github.io/

import pandas as pd
from colorama import Fore, init

init(autoreset=True)  # 配置colorama颜色自动重置，否则得手动设置Style.RESET_ALL


def txtLineList(fileName):
    """
    提取txt文件的每行数据，输出字符串列表
    :param fileName: 待提取数据的txt文件
    :return: 字符串列表
    """
    resultList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            resultList.append(line.strip('\n'))  # 去除文本中的换行符
    return resultList


def compareTxtFile(filePath1, filePath2):
    """
    比较两份由不同findstr或ag搜索命令查询出来的txt结果文件，输出共同包含的文件路径列表
    :param filePath1: 待分析的文件1的路径
    :param filePath2: 待分析的文件2的路径
    :return: 输出共同包含的文件路径列表
    """
    print(Fore.BLUE + "[*]Start analyze…")
    fileList1 = txtLineList(filePath1)
    fileList2 = txtLineList(filePath2)
    resultList = []
    middleList = []
    for line in fileList1:
        middleList.append(line.split(":")[0])  # 取每行第一个冒号之前的数据
    for line in fileList2:
        file = line.split(":")[0]
        if file in middleList:
            if file not in resultList:
                resultList.append(file)
                print(Fore.GREEN + "[+]" + file)
    print(Fore.BLUE + "[*]Done.Enjoy it!")
    return resultList


def writeTxtToXlsx(txtPath, xlsxPath):
    """
    将txt文件转换成xlsx格式的表格
    :param txtPath: 待转换的txt文件路径
    :param xlsxPath: 输出的xlsx文件路径
    :return: null
    """
    dataSource = {}
    dictCol1List = []
    dictCol2List = []
    lineList = txtLineList(txtPath)
    # 目标行数据样例：“AirTouch.apk\sources\defpackage\ih.java:    public boolean[] getBooleanArrayExtra(String str) {”
    for line in lineList:
        dictCol1List.append(line.split(":")[0])  # 截取每行数据第一个冒号前的数据
        dictCol2List.append(line.split(":")[1].lstrip(" "))  # 截取每行数据第一个冒号后的数据，同时去掉字符串左侧空格
    # 设置xlsx表格每列数据的源数据列表
    dataSource["filePath"] = dictCol1List
    dataSource["codeResult"] = dictCol2List
    # print(dataSource)
    print(Fore.BLUE + "[*]Start write data…")
    writer = pd.ExcelWriter(xlsxPath)
    dataFrame = pd.DataFrame(dataSource)
    dataFrame.to_excel(writer, sheet_name="sheet1")
    writer.close()  # 保存writer中的数据至excel
    print(Fore.BLUE + "[*]Done.Enjoy it!")


def copyRight():
    print(Fore.YELLOW + "************** CopyRight ****************")
    print(Fore.GREEN + "             Welcome to use               ")
    print(Fore.GREEN + "     Author: Tr0e                         ")
    print(Fore.GREEN + "     Github: https://github.com/Tr0e      ")
    print(Fore.GREEN + "     Blog  : https://tr0e.github.io       ")
    print(Fore.YELLOW + "*****************************************")


if __name__ == '__main__':
    copyRight()
    # compareTxtFile("data/output1.txt", "data/output2.txt")
    writeTxtToXlsx("data/output.txt", "data/output.xlsx")
    exit(0)
