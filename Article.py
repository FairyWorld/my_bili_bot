# -*- coding: utf-8 -*-
import json, re, time, os
import requests
from BiliClient import Article

def main_handler():
    
    sessdata: str = os.environ.get('SESSDATA', None)
    bili_jct: str = os.environ.get('BILI_JCT', None)
    
    #获取secrets里的cookie
    cookies = { 
        "SESSDATA": sessdata,
        "bili_jct": bili_jct
    }
    
    # 执行的次数不要太多，b站限制每天发布专栏的次数

    num = 12 #只爬取18张图,可以调大，如果中间网络异常会丢失几张图，最终数量可能达不到, 至少要3张图片

    #创建B站专栏
    article = Article(cookies, "每日Pixiv美图") #创建B站专栏草稿,并设置标题
    content = Article.Content() #创建content类编写文章正文
    content.startP().add('所有图片均转载于').startB().add('网络').endB().add('，如有侵权请联系我，我会立即').startB().add('删除').endB().endP().br()
        #开始一段正文    添加正文           开始加粗  加粗文字  结束加粗                                                           结束一段文字  换行

    #下面开始爬取P站图片
    datas = []
    headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                "Referer": "https://www.pixiv.net/",
                "Accept-Encoding": "gzip, deflate, br",
                "Cookie": "PHPSESSID=47159460_0LAKIXToAy9kTW00isF5hWA4uQw6CfYh"
            }
    session = requests.session()
    list = session.get("https://www.pixiv.net/ajax/top/illust?mode=all&lang=zh", headers=headers).json()["body"]["thumbnails"]["illust"]
    for i in range(num):
        id = list[i]["id"]
        title = list[i]["title"]
        url = f'https://www.pixiv.net/artworks/{id}'
        try:
            res = session.get(url, headers=headers)
            findurl = re.findall('.*?\"original\":\"(.*?)\"\}.*',res.text)[0]
            res = session.get(findurl, headers=headers) #这里得到P站图片
            ret = article.articleUpcover(res.content) #这里上传到B站
            tourl = ret["data"]["url"]
            tourl = tourl.replace("http", "https")
            datas.append({"url":tourl,"title":title}) #将上传到B站的url和图片的标题保存
        except:
            continue
        time.sleep(3)

    i = 0
    for x in datas:
        i += 1
        content.startP().startB().add(f'{i}.').endB().endP().picUrl(x["url"], x["title"])
                                #序号加粗                      插入图片和图片标题

    article.setContent(content) #将文章内容保存至专栏
    article.setImage(datas[0]["url"])  #将第一张图片设置为专栏缩略图
    article.setCategory(4)  #将专栏分类到"动画 → 动漫杂谈"
    article.setOriginal(0)  #设置为非原创专栏,因为是转载的
    article.save() #保存专栏至B站草稿箱
    article.submit() #发布专栏，注释掉后需要到article.getAid(True)返回的网址去草稿箱手动提交

main_handler()



