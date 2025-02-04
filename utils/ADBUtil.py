import random
import sys
import adbutils
import subprocess
import os

from utils.ImageUtil import readImageFromBytes
from utils.LogUtil import Log

adb = adbutils.AdbClient(host="127.0.0.1", port=5037)


class ADBUtil:

    device = None
    rplc = b"\r\n"
    test = False

    def getScreen(self, savePath=None):
        binary_screenshot = b""

        if self.device is not None:
            stream = self.device.shell(["screencap", "-p"], stream=True)
            
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    break
                binary_screenshot += chunk

            stream.close()

        if not self.test:
            try:
                readImageFromBytes(binary_screenshot.replace(self.rplc, b"\n"))
            except Exception:
                self.rplc = b"\r\r\n"
            finally:
                self.test = True

        binary_screenshot = binary_screenshot.replace(self.rplc, b"\n")

        if savePath is not None and len(binary_screenshot) != 0:
            dirs = os.path.dirname(savePath)

            if not os.path.exists(dirs):
                os.makedirs(dirs)

            with open(savePath, "wb") as f:
                f.write(binary_screenshot)

        return binary_screenshot

    def touchScreen(self, area):
        if self.device is not None:
            self.device.click(
                random.randrange(area[0], area[2]),
                random.randrange(area[1], area[3])
            )

    def swipeScreen(self, x1, y1, x2, y2):
        if self.device is not None:
            self.device.swipe(x1, y1, x2, y2, random.uniform(0.5, 1.0))

    def setDevice(self, serial):
        # 用户没有指定设备
        if serial is None:
            devices = adb.device_list()
            if len(devices) == 0:
                Log.error("未检测到设备连接")
                serial = "127.0.0.1:5555"
                serial = input("请输入设备IP和端口进行连接，默认127.0.0.1:5555\n")
                out = adb.connect(serial, timeout=3)
                Log.info(out)
            else:
                Log.info("检测到已连接的设备，请输入序号指定要连接的设备:")
                for i in range(0, len(devices)):
                    print("[{}] - {}".format(i, devices[i]._serial))
                try:
                    print("[-1] - 手动输入设备ip和端口进行连接")
                    index = int(input())
                    if index == -1:
                        serial = "127.0.0.1:5555"
                        serial = input("请输入设备IP和端口进行连接，默认127.0.0.1:5555\n")
                        out = adb.connect(serial, timeout=3)
                        Log.info(out)
                    else:
                        serial = devices[index]._serial
                except ValueError:
                    Log.error("请输入正确的序号!!!")
                    sys.exit()
        self.device = adbutils.AdbDevice(adb, serial=serial)
        Log.info("设备serial : {}".format(self.device._serial))
        try:
            Log.info("设备信息 : {}".format(self.device.prop))
        except adbutils.errors.AdbError:
            Log.error("获取设备信息失败")
            sys.exit()

    def __init__(self):
        if getattr(sys, "frozen", None):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(__file__)
        adbPath = os.path.join(basedir, "") + r"adb;"
        os.environ['PATH'] = adbPath + os.environ['PATH']


adbUtil = ADBUtil()
