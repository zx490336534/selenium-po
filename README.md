# Selenium的PO模型封装
使用`Yaml`文件进行元素信息的管理

## 安装

> Github地址：https://github.com/zx490336534/selenium-po

```shell
$ pip install selenium-po
```

# 使用方法
## 创建一份yaml

代码中使用的是`name`后的内容，实际页面元素定位使用的`value`中的内容，方便后续统一维护

```yaml
pages:
  - page:
      pageName: index
      desc: 首页
      locators:
        - {desc: "搜索栏",type: "id",value: "kw",timeout: 3, name: "index_input"}
        - {desc: "查询按钮",type: "id",value: "su",timeout: 3, name: "index_search"}
  - page:
      pageName: news
      desc: 新闻
      locators:
        - {desc: "搜索栏",type: "id",value: "ww",timeout: 3, name: "news_input"}
        - {desc: "查询按钮",type: "id",value: "s_btn_wr",timeout: 3, name: "news_search"}
```

## 创建一个页面操作对象

```python
import os
import time
from selenium_po.elementoperator import ElementOperator

path = os.path.dirname(os.path.abspath(__file__))


class BaiDuIndexAction(ElementOperator):
    def __init__(self, path=f"{path}/pages.yaml", file_name='index', driver=None):
        super(BaiDuIndexAction, self).__init__(path, file_name, driver)
        self.url = 'http://www.baidu.com'


class BaiDuNewsAction(ElementOperator):
    def __init__(self, path=f"{path}/pages.yaml", file_name='news', driver=None):
        super(BaiDuNewsAction, self).__init__(path, file_name, driver)
        self.url = 'http://news.baidu.com/'

```

## 测试

```python
if __name__ == '__main__':
    baidu = BaiDuIndexAction()
    baidu.open(baidu.url, baidu.index_input)
    baidu.input(baidu.index_input, "python")
    baidu.click(baidu.index_search)
    time.sleep(2)
    baidu.screenshot_pic("1.png")
    # baidu.close()
    baidu_news = BaiDuNewsAction(driver=baidu.driver)
    baidu_news.open(baidu_news.url, baidu_news.news_input)
    baidu_news.input(baidu_news.news_input, "python新闻")
    baidu_news.click(baidu_news.news_search)
    time.sleep(2)
    baidu_news.screenshot_pic("2.png")
    baidu_news.close()
```

### 输出
```shell
往「首页_搜索栏」输入「python」
点击「首页_查询按钮」
往「新闻_搜索栏」输入「python新闻」
点击「新闻_查询按钮」
```

### 截图

![测试截图](https://tva1.sinaimg.cn/large/007S8ZIlly1ghzfb4xq42j31lb0u01kx.jpg)

![测试截图2](https://tva1.sinaimg.cn/large/007S8ZIlly1ghzgmi6volj31lb0u0e1h.jpg)



公众号：「测试游记」

![公众号](https://tva1.sinaimg.cn/large/007S8ZIlly1ghzfczgkauj30rx0wcn01.jpg)