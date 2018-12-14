import requests
import urllib3
from PIL import Image
from bs4 import BeautifulSoup
import cv2
import tesserocr
import re
from private_constants import MESSAGE_USERNAME, MESSAGE_PASSWORD

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__author__ = "guishenyouhuo"


class MessageProcess:
    def __init__(self, request, header, code_path):
        self.req = request
        self.header = header
        self.code_path = code_path

    def get_verify_code(self):
        code_url = "https://user.hao315.com/ValidateCode.php"
        response = self.req.get(code_url, headers=self.header, verify=False)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            with open(self.code_path, 'wb') as fn:
                fn.write(response.content)
                print("验证码图片下载成功！")
                return True
        else:
            print("验证码图片下载失败！正在重试...")
            self.get_verify_code()

    def recognsize_image(self):
        img = Image.open(self.code_path)
        # 将图片变成灰色
        img_gray = img.convert('L')
        img_gray.save('../images/code_gray.png')
        # 转成黑白图片
        img_black_white = img_gray.point(lambda x: 0 if x > 200 else 255)
        img_black_white.save('../images/code_black_white.png')
        # opencv处理
        img_cv = cv2.imread('../images/code_black_white.png')
        # 灰值化
        im = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        # 二值化
        cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 1)
        # 降噪处理
        img_point, result_name = interference_point(im)
        img_result = Image.open(result_name)
        return tesserocr.image_to_text(img_result)

    def login_process(self, code_text, hasType):
        login_url = 'https://user.hao315.com/login2/login'
        data = {
            'username': MESSAGE_USERNAME,
            'password': MESSAGE_PASSWORD,
            'verify': code_text,
        }
        if hasType:
            data['type'] = '2'
        result = self.req.post(url=login_url, data=data, headers=self.header, verify=False)
        return result.json()

    def get_message(self):
        message_url = 'https://user.hao315.com/jiuyimr/uidly?starttime=2018-12-13&endtime=2018-12-14'
        resp = self.req.get(message_url, headers=self.header, verify=False)
        resp.encoding = 'utf-8'
        # 请求成功才进行处理
        if resp.status_code == requests.codes.ok:
            bs = BeautifulSoup(resp.text, 'html.parser')
            data_table = bs.find("table", class_='pure-table table')
            tr_arr = data_table.find_all('tr')
            print("留言列表：")
            for tr in tr_arr:
                td_arr = tr.find_all('td')
                if td_arr is None or len(td_arr) == 0:
                    continue
                print(td_arr[1].get_text().strip() + ", " + td_arr[2].get_text().strip() + ", "
                      + td_arr[5].get_text().strip() + ", " + td_arr[8].get_text().strip())
                print('----------------------------------')


# 噪点处理
def interference_point(img):
    filename = '../images/code_result.png'
    h, w = img.shape[:2]
    # 遍历像素点进行处理
    for y in range(0, w):
        for x in range(0, h):
            # 去掉边框上的点
            if y == 0 or y == w - 1 or x == 0 or x == h - 1:
                img[x, y] = 255
                continue
            count = 0
            if img[x, y - 1] == 255:
                count += 1
            if img[x, y + 1] == 255:
                count += 1
            if img[x - 1, y] == 255:
                count += 1
            if img[x + 1, y] == 255:
                count += 1
            if count > 2:
                img[x, y] = 255
    cv2.imwrite(filename, img)
    return img, filename


if __name__ == "__main__":
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }
    req = requests.session()
    mp = MessageProcess(req, headers, '../images/msg_code.png')
    try_count = 0
    code_text = None
    while True:
        while code_text is None or len(code_text) != 4:
            try:
                mp.get_verify_code()
            except Exception:
                print("获取验证码异常，正在重试...")
                mp.get_verify_code()
            code_text = mp.recognsize_image()
            print("识别到原始验证码：", end=code_text)
            code_text = re.sub('[^0-9a-zA-Z]+', '', code_text)
        print("处理后的验证码：", end=code_text)
        login_result = mp.login_process(code_text, True)
        print("登录返回结果: ")
        print(login_result)
        if login_result['success']:
            mp.get_message()
            break
        code_text = None
        try_count += 1
        if try_count > 10:
            print("重试次数达到最大，退出！")
            break
