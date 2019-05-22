import requests
import time
import csv
from bs4 import BeautifulSoup

#功能：打开py文件同级下含有公司名称的txt文件，搜索公司相关信息后存储到csv文件中
#headers包含Cookike，需要登陆之后从浏览器里获取。可以绕开登陆验证，但是一定时间内的访问次数仍然会受到限制
headers = {
        'Cookie': 'zg_did=%7B%22did%22%3A%20%2216ac04871e0320-0eb5d115f1f70f-f353163-144000-16ac04871e16cd%22%7D; UM_distinctid=16ac0487254195-053e0d1d6299f1-f353163-144000-16ac0487255867; _uab_collina=155800413514397024607025; acw_tc=da5bdda515580041316712951edb6ccd3c8d44bcc642f106f3342720c9; QCCSESSID=i9tvrd2nvmcb65rt14bv9k7944; hasShow=1; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1558077901,1558339674,1558339750,1558512843; CNZZDATA1254842228=1466785710-1557999208-https%253A%252F%252Fwww.baidu.com%252F%7C1558528537; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1558531982; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201558531980262%2C%22updated%22%3A%201558532003610%2C%22info%22%3A%201558004134380%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.qichacha.com%22%2C%22cuid%22%3A%20%229f7b60922a8b1766b40356fe85c160ef%22%7D',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}

def file_create():
    #初始化csv文件作为存储文档
    with open('qiyexinxi.csv','w',encoding='utf-8') as csvfile:
        fieldnames = ['公司名称', '行业', '经营范围']
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()

def url_generator():
    #读取存储有待爬取公司url的txt文件，与基础url拼接构造搜索用url
    enterprise_list = []
    with open('list.txt', 'r', encoding="utf-8") as f:
        entlist = f.readlines()
    for i in entlist:
        line = i.rstrip()
        enterprise_list.append(line)
    baseurl = 'https://www.qichacha.com/search?key='
    search_urls = []
    for i in enterprise_list:
        search_urls.append(baseurl+i)
    return search_urls

def web_search(url):
    #使用get方法输入公司名进行查询，返回搜索结果的第一条中此公司的url作为下一步解析公司主页的url
    #如果搜索结果不为空，就默认第一个公司就是要找的公司，此处使用了bs的循环嵌套功能，非常好用
    url2 = requests.get(url, headers=headers)
    soup = BeautifulSoup(url2.content, 'lxml')
    try :
        search_result = soup.find(id='search-result').find_all(class_="ma_h1")[0].attrs['href']
        com_url = 'https://www.qichacha.com/' + search_result
    except :
        com_url='error'
    return com_url

def content_parser(url):
    #解析公司主页url，返回相关结果，try，except防止出现网页结构改变
    html = requests.get(url,headers=headers)
    soup = BeautifulSoup(html.content,'lxml')
    try:
        industry = soup.find(id='Cominfo').find_all(class_='ntable')[1].find_all('tr')[4].find_all('td')[3].get_text()
    except:
        industry = 'Info Not Found'
    try:
        business = soup.find(id='Cominfo').find_all(class_='ntable')[1].find_all('tr')[10].find_all('td')[1].get_text()
    except:
        business = 'Info Not Found'
    return industry.strip(),business.strip()

def main():
    #初始化文件
    file_create()
    for i in url_generator()[1:]:
        com_url = web_search(i)
        #print(url_generator().index(i))
        time_start = time.time()
        if com_url=='error':
            print('URL'+str(i)+'错误！')
            industry = 'Error'
            business = 'Error'
        else:
            result = content_parser(com_url)
            industry = result[0]
            business = result[1]
            print('成功，爬取进度:' + str((url_generator().index(i))) + '/' + str((len(url_generator()) - 1)) + ',耗时:' + str(
                time_end - time_start) + 's')
        com_name = i[36:]
        # 以csv格式写入保存
        with open('qiyexinxi.csv', 'a', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['公司名称', '行业', '经营范围']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(
                {'公司名称': com_name,
                 '行业': industry, '经营范围': business})
        time_end = time.time()
        #睡眠3秒防止单位时间内访问次数过高
        time.sleep(3)

main()