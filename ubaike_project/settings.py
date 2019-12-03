# -*- coding: utf-8 -*-
BOT_NAME = 'ubaike_project'
SPIDER_MODULES = ['ubaike_project.spiders']
NEWSPIDER_MODULE = 'ubaike_project.spiders'

DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'ubaike_project.middlewares.LocalRetryMiddlerware': 300,
        'ubaike_project.middlewares.RandomUserAgentMiddleware': 200,
        # 'ubaike_project.middlewares.UserAgentMiddleware': 200,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,  # 禁用默认的代理
        'ubaike_project.middlewares.RandomProxiesMiddlerware': 350,
        # 'ubaike_project.middlewares.RandomProxyUserPwdMiddlerware': 350,
}

ITEM_PIPELINES = {
   'ubaike_project.pipelines.UbaikeProjectPipeline': 400,
   'ubaike_project.pipelines.MysqlPipeline': 450,
   'ubaike_project.pipelines.MongoPipeline': 430,
   # 'ubaike_project.pipelines.MysqlTwistedPipeline': 450,

}
# --------------scrapy-存储到mongodb设置-----------------#
MONGO_URI = '127.0.0.1'
MONGO_DATA_BASE = 'db_ubaike'
# --------------scrapy-存储到mysql设置-----------------#
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'company_info'
DB_CHARSET = 'utf8'

# --------------scrapy-爬取 设置-----------------#
ROBOTSTXT_OBEY = False
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2
# DOWNLOAD_DELAY = 0.05
# COOKIES_ENABLED = True
RETRY_ENABLED = True
RETRY_TIMES = 9  # 重试次数
REDIRECT_ENABLED = False  # 禁止重定向,默认是True
DOWNLOAD_TIMEOUT = 20  # 下载超时时间默认180
# REACTOR_THREADPOOL_MAXSIZE = 20  # 增加处理DNS查询的线程数
LOG_LEVEL = 'INFO'


# --------------scrapy-redis下载引擎,调度器,过滤等等设置-----------------#
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"
SCHEDULER_QUEUE_CLASS = 'scrapy_redis_bloomfilter.queue.SpiderPriorityQueue'
# Number of Hash Functions to use, defaults to 6
BLOOMFILTER_HASH_NUMBER = 6
# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
BLOOMFILTER_BIT = 32
# Persist
SCHEDULER_PERSIST = True
# SCHEDULER_FLUSH_ON_START = True  # 是否在开始之前清空，调度器和去重记录
# REDIS_URL = 'redis://root:axy@2019@localhost:6379/3'


# --------------scrapy-请求头 设置-----------------#
RANDOM_UA_TYPE = "random"
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
    "Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
]


# --------------redis连接配置-----------------#
# 代理连接配置
REDIS_PROXIES_HOST = 'proxyhost'
REDIS_PROXIES_PORT = 6379
REDIS_PROXIES_PASSWORD = ''
REDIS_PROXIES_DB = 15
# 存储连接配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
REDIS_DB = 3
# 指定 redis链接密码，和使用哪一个数据库,可以在scrapy_redis里面的defults文件查看
REDIS_PARAMS = {
    "password": "",
    "db": 3,
}

# --------------elasticsearch连接配置-----------------#
ES_HOST = '127.0.0.1'
ES_PORT = 9200
ES_USERNAME = ''
ES_PASSWORD = ''
INDEX_NAME = 'cf_index_db'
INDEX_TYPE = 'xzcf'
