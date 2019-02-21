import requests, sqlite3, re

class ProcessDataTool(object):
    """
    数据处理的工具类：工具类中一般不写__init__初始化属性，只封装工具方法对数据进行操作。工具类中的方法一般是以类方法居多。
    """
    @classmethod
    def process_data(cls, data_tuple):
        """
        对原始的元组数据处理完成，返回一个新的元组
        :param data_tuple:
        :return:
        """
        # print(data_tuple)
        # 经过输出，发现用户昵称和段子内容需要处理特殊字符，将\n和<br/>从原始字符串中删除。
        p1 = re.compile(r'\n', re.S)
        p2 = re.compile(r'<br/>', re.S)

        nick_name = data_tuple[0]
        # 利用p1这个正则表达式，从nick_name字符串中匹配\n，并将其替换为''这个空字符串
        nick_name = re.sub(p1, '', nick_name)

        content = data_tuple[2]
        # 处理内容中的换行符\n
        content = re.sub(p1, '', content)
        # 处理内容的的<br/>
        content = re.sub(p2, '', content)

        return nick_name, data_tuple[1], content, data_tuple[3], data_tuple[4]

class DBTool(object):
    """
    数据库工具类：
    """
    connect = cursor = None

    @classmethod
    def connect_cursor(cls):
        cls.connect = sqlite3.connect('qsbk.db')
        cls.cursor = cls.connect.cursor()

    @classmethod
    def insert_data(cls, data):
        insert_sql = 'INSERT INTO qsbk(nick_name, level, content, smail_count, comment_count) VALUES (?, ?, ?, ?, ?)'
        cls.cursor.execute(insert_sql, data)
        cls.connect.commit()

    @classmethod
    def close_connect_cursor(cls):
        cls.cursor.close()
        cls.connect.close()

class QSBKSpider(object):
    """
    爬虫类
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
        }

    def get_list_page(self, page_num):
        """
        获取列表页源代码
        :param page_num: 页码
        :return:
        """
        url = ''
        try:
            url = 'https://www.qiushibaike.com/hot/page/{}/'.format(page_num)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                # 返回网页源代码字符串，交给下一个函数进行解析
                return response.text
            else:
                # 202: 表示对方服务器已经成功的接受了GET请求，但是并没有给与响应，如果多次尝试一直都是202，说明遭遇了发爬虫的限制了。
                print('状态码异常：{}，url地址：'.format(response.status_code, url))
                return None
        except Exception as e:
            print('当前url: {}请求异常，异常原因：{}'.format(url, e))
            return None

    def parse_list_page(self, html):
        """
        解析列表页源代码
        :param html:
        :return:
        """
        pattern = re.compile(r'<div class="article.*?<div class="author clearfix">.*?<h2>(.*?)</h2>.*?<div class="articleGender.*?">(.*?)</div>.*?<span>(.*?)</span>.*?<span class="stats-vote">.*?<i class="number">(.*?)</i>.*?<span class="stats-comments">.*?<i class="number">(.*?)</i>', re.S)
        datas = re.findall(pattern, html)
        for data_tuple in datas:
            # 将原始数据交给工具类进行数据的整理。
            new_data_tuple = ProcessDataTool.process_data(data_tuple)
            DBTool.insert_data(new_data_tuple)

if __name__ == '__main__':

    DBTool.connect_cursor()

    spider = QSBKSpider()
    html = spider.get_list_page(1)
    if html:
        spider.parse_list_page(html)
    else:
        pass

    DBTool.close_connect_cursor()
