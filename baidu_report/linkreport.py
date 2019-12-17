#!/usr/bin/python
# encoding: utf-8

import redis
import urllib2
import MySQLdb
import traceback

mysql_connect = MySQLdb.connect('127.0.0.1', 'root', 'fly2010love!@#$', 'flyblog')
master_client = redis.Redis(host='127.0.0.1', password='fly2010love', port=7379, db=0)  # 7379

REPORT_URL = "http://data.zz.baidu.com/urls?site=www.flyfifi.cn&token=vfqMduuYhmM4FI1Q"
UPDATE_URL = "http://data.zz.baidu.com/update?site=www.flyfifi.cn&token=vfqMduuYhmM4FI1Q"

ARTICLE_BASE_URL = "http://www.flyfifi.cn/blog/detail/%d/"
COLUMN_BASE_URL = "http://www.flyfifi.cn/blog/article_column/%d/"
PAGE_BASE_URL = "http://www.flyfifi.cn/blog/?page=%d"

REPORT_ARTICLES_HASH = "baidu:report:articles"
REPORT_COLUMNS_HASH = "baidu:report:columns"


def send_post_request(urls, baiduurl):
    body = ""
    if urls and len(urls) > 0:
        for url in urls:
            body = body + url + "\n"
    else:
        return

    response = None
    req = urllib2.Request(baiduurl, body)  # 生成请求的完整数据

    try:
        response = urllib2.urlopen(req, timeout=5)
        code = response.getcode()
        res = response.read()
        print "res: " + str(res)
    except urllib2.URLError as e:
        print e
        if hasattr(e, 'code'):
            print 'Error code:', e.code
            # print e.read()
            print e.geturl()
            print e.info()
        if hasattr(e, 'reason'):
            print 'Reason:', e.reason
    except:
        pass
    finally:
        if response:
            response.close()


#获取所有的博文ID列表
def query_article_ids():
    article_list = []
    mysql_client = mysql_connect.cursor()
    sql = 'SELECT id FROM blog_articlepost;'
    try:
        # 执行SQL语句
        mysql_client.execute(sql)
        # 获取所有记录列表
        results = mysql_client.fetchall()
        for row in results:
            article_list.append(int(row[0]))

    except:
        traceback.print_exc()
    finally:
        return article_list

#获取所有分类的ID列表
def query_articlecolumn_ids():

    column_list = []
    mysql_client = mysql_connect.cursor()
    sql = 'SELECT id FROM blog_articlecolumn;'
    try:
        # 执行SQL语句
        mysql_client.execute(sql)
        # 获取所有记录列表
        results = mysql_client.fetchall()
        for row in results:
            column_list.append(int(row[0]))

    except:
        traceback.print_exc()
    finally:
        return column_list

#判断是否已提交过, False:表示未提交过
def get_report_state(id, key):
    state = master_client.hget(key, id)
    if state == None or int(state) <= 0:
        return False

    return True


#组装成博文的url地址
def pack_article_urls(ids):
    urls = []
    if ids and len(ids) > 0:
        for id in ids:
            if not get_report_state(id, REPORT_ARTICLES_HASH):
                urls.append(str.format(ARTICLE_BASE_URL % id))
                record_report_state(id, REPORT_ARTICLES_HASH)

    return urls

#组装成分类的url地址
def pack_column_urls(ids):
    urls = []
    if ids and len(ids) > 0:
        for id in ids:
            if not get_report_state(id, REPORT_COLUMNS_HASH):
                urls.append(str.format(COLUMN_BASE_URL % id))
                record_report_state(id, REPORT_COLUMNS_HASH)

    return urls

#记录已提交过
def record_report_state(id, key):
    master_client.hset(key, id, 1)

if __name__ == '__main__':
    ids = query_article_ids()
    urls = pack_article_urls(ids)

    ids = query_articlecolumn_ids()
    urls = urls + pack_column_urls(ids)

    for i in range(1, 16):
        urls.append(str.format(PAGE_BASE_URL % i))

    send_post_request(urls, REPORT_URL)

    #urls = ["http://www.flyfifi.cn"]
    #send_post_request(urls, UPDATE_URL)

    print urls
