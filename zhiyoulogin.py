import requests
# LWPCookieJar()可以自动将响应头中Set-Cookie中的值保存下来，不需要再单独解析了。
from http.cookiejar import LWPCookieJar

class LoginSpider(object):
    def __init__(self):
        self.url = 'http://kaoshi.zhiyou900.com:8888/edustu/login/login.spr'
        # 初始化Session类的对象，接下来的请求就不再使用requests了，而是使用self.session来发送GET/POST请求。
        self.session = requests.Session()
        # filename：当登录成功之后，将登录之后的cookie保存在这个文件中。后续请求就可以直接使用这个cookie访问，不用频繁的登录了。
        self.session.cookies = LWPCookieJar(filename='cookies.txt')

    def index(self):
        """ 
        请求首页url，获取学员的信息
        :return:
        """
        # 在访问这个首页的时候，先从本地文件cookies.txt读取登录之后的cookie信息。如果本地cookie文件不存在，那么需要先登录获取cookie。
        try:
            # ignore_expires和ignore_discard一定要设置，否则可能会导致最终保存的cookie信息是不完整的。
            # session.cookies.load表示将本地文件中的cookie信息全部加载的session，当使用session发送请求的时候，就会自动携带这些cookie。
            self.session.cookies.load(filename='cookies.txt', ignore_expires=True, ignore_discard=True)
            print('Cookie加载成功')
            response = self.session.get(url='http://kaoshi.zhiyou900.com:8888/edustu/me/edu/meda.spr')
            if response.status_code == 200:
                # 请求成功，并且cookie是可用的
                print(response.text)
            else:
                # 可能是Cookie不能使用了，此时需要重新登录，生成新的cookie信息，并保存在cookies.txt文件中
                result = self.login()
                if result == 'ok':
                    self.index()
        except Exception as e:
            # 本地文件不存在，此时在进行模拟登录
            print('Cookie加载失败')
            result = self.login()
            if result == 'ok':
                self.index()

    def login(self):
        """
        模拟登录函数。
        :return:
        """
        print('开始登录')
        login_url = 'http://kaoshi.zhiyou900.com:8888/edustu/login/login.spr'
        post_data = {
            'j_username': '15516338825',
            'j_password': '123456'
        }
        # 这个POST请求主要就是为了Set-Cookie，但是self.session会自动解析这些Cookie，并保存起来。
        response = self.session.post(url=login_url, data=post_data)
        if response.status_code == 200:
            # 登录成功，将登录之后的所有的Cookie保存在cookie.txt文件中。
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            return 'ok'
        else:
            return 'error'


if __name__ == '__main__':
    obj = LoginSpider()
    obj.index()
