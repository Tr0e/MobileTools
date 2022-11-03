# @File  : fridaHook
# @Time  : 2022/10/29 23:12
# @Author: Tr0e
# @Blog  : https://tr0e.github.io/
import frida
import sys
from colorama import Fore, init

init(autoreset=True)

jsCode = """
if(Java.available){
    Java.perform(function(){
        console.warn("[*]Starting Hook Script.");
        //目标Hook类
        var hookClass = Java.use("com.Tr0e.hacker.util.MyUtil");        
        //HooK目标函数并重写逻辑
        hookClass.fridaTest.overload('java.lang.String').implementation=function(arg1){
            //打印java函数的调用栈信息
            send("[+]Java调用栈信息如下：\\n" + Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Throwable").$new()));
            //修改目标函数的入参
            console.log("[+]Origin arg is: " + arg1);
            arg1 = "admin123"  
            console.log("[+]Modified arg is: " + arg1);
            var result = this.fridaTest(arg1);
            send("Hook end.");
            //此处注意如果被Hook的目标函数有返回值，一定要return其返回值
            return result;
        }
    }); 
}
"""

bankHookJs = """
setImmediate(function() {
    Java.perform(function() {
        console.log("[*] Starting Hook Script.");
        var hookSM4 = Java.use("cn.*****.encrypt.utils.sm4.SM4Utils");
        //hook加密函数
        hookSM4.encryptData.overload('java.lang.String').implementation = function(arg1){
            console.warn("[*] 原始的请求包如下:");
            console.log(arg1);
            //修改请求包参数  
            /*
            if (arg1.indexOf("0.01") >= 0) {
                arg1 = arg1.toString().replace(/0.01/g, "-0.01");
                console.error("********************************修改后请求包如下*********************************");
                console.log(arg1);
            }	          
            */								
            //修改完参数以后再调用原方法发送请求
            var result = this.encryptData(arg1);
            return result;					
        }		
        //hook解密函数	
        hookSM4.decryptData.overload("java.lang.String").implementation = function(arg1){
            //修改完参数以后再调用原方法发送请求
            var result = this.decryptData(arg1);
            console.error("[*] 原始的响应包如下：");
            console.log(result + "\n");
            /*
            if (result.indexOf("403") >= 0) {
                result = result.toString().replace(/403/g, "200");
                console.error("********************************修改后响应包如下*********************************");
                console.log(result);
            }*/
            return result;
        }		
    }); 
});
"""


def on_message(message, data):
    if message['type'] == 'send':
        getData = message['payload']
        if "end" in getData:
            print("[*]Message from js:{0}".format(getData))
            print(Fore.GREEN + "*****************************************")
        elif "Java调用栈" in getData:
            print(Fore.YELLOW + getData.strip('\n'))
    elif message['type'] == 'error':
        print(Fore.RED + message['description'])
    else:
        print(Fore.YELLOW + message)


def copyRight():
    print(Fore.YELLOW + "************** CopyRight ****************")
    print(Fore.GREEN + "             Welcome to use               ")
    print(Fore.GREEN + "     Author: Tr0e                         ")
    print(Fore.GREEN + "     Github: https://github.com/Tr0e      ")
    print(Fore.GREEN + "     Blog  : https://tr0e.github.io       ")
    print(Fore.YELLOW + "*****************************************")


if __name__ == '__main__':
    copyRight()  # 打印作者信息
    session = frida.get_usb_device().attach('MyPoc')  # 查找USB设备并附加到目标进程，'MyPoc'为通过frida-ps -U命令查询到的目标进程的APP名称
    script = session.create_script(jsCode)  # 在目标进程里创建脚本
    script.on('message', on_message)  # 注册消息回调
    script.load()  # 加载创建好的javascript脚本
    sys.stdin.read()  # 读取系统输入
