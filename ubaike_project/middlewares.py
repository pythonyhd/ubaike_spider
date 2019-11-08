# -*- coding: utf-8 -*-
import logging
import random
import redis
import base64
import time
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.python import global_object_name
from scrapy.utils.response import response_status_message
from fake_useragent import UserAgent
from ubaike_project import settings
logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware(object):
    """
    利用fake_useragent生成随机请求头
    """
    def __init__(self, ua_type):
        self.ua_type = ua_type
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            ua_type=crawler.settings.get('RANDOM_UA_TYPE', 'random')
        )

    def process_request(self, request, spider):
        def get_user_agent():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault(b'User-Agent', get_user_agent())
        # logger.debug("FakeUserAgent Successful:{}".format(request.headers))


class UserAgentMiddleware(object):
    """
    从settings配置文件读取user_agent
    """
    def __init__(self, crawler):
        super(UserAgentMiddleware, self).__init__()
        self.user_agent_list = crawler.settings.get('USER_AGENTS', [])

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        request.headers.setdefault(b'User-Agent', user_agent)
        # logger.debug("UserAgent:{}".format(user_agent))


class RandomProxiesMiddlerware(object):
    """
    没有账号密码的代理IP
    """
    def __init__(self, crawler):
        super(RandomProxiesMiddlerware, self).__init__()
        self.redis_client = redis.StrictRedis(
            host=crawler.settings.get('REDIS_PROXIES_HOST'),
            port=crawler.settings.get('REDIS_PROXIES_PORT', 6379),
            password=crawler.settings.get('REDIS_PROXIES_PASSWORD', ''),
            db=crawler.settings.get('REDIS_PROXIES_DB', 15),
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def delete_proxy(self, proxy):
        """
        删除代理
        """
        self.redis_client.srem("proxies", proxy)

    def process_request(self, request, spider):
        ip_port = self.redis_client.srandmember('proxies')
        proxies = {
            'http:': 'http://{}'.format(ip_port.decode('utf-8')),
            'https:': 'https://{}'.format(ip_port.decode('utf-8')),
        }
        if request.url.startswith('http://'):
            request.meta['proxy'] = proxies.get('http:')
            # logger.debug('http链接,ip:{}'.format(request.meta.get('proxy')))
        else:
            request.meta['proxy'] = proxies.get('https:')
            # logger.debug('https链接,ip:{}'.format(request.meta.get('proxy')))

    def process_response(self, request, response, spider):
        if response.url == 'https://www.ubaike.cn/book.html':
            return request
        return response

    def process_exception(self, request, exception, spider):
        # print("格式化后的对象:{}".format(repr(exception)))
        if "ConnectionRefusedError" in repr(exception):
            proxy = request.meta.get("proxy")
            if proxy:
                proxy = proxy.split("//")[1]
                self.delete_proxy(proxy)
                logger.info("目标计算机积极拒绝,删除代理 - {} - 请求的url - {}".format(proxy, request.url))
            return request

        elif "TCPTimedOutError" in repr(exception):
            proxy = request.meta.get('proxy')
            if proxy:
                proxy = proxy.split('//')[1]
                self.delete_proxy(proxy)
                logger.info("连接方在一段时间后没有正确答复或连接的主机没有反应,删除代理 - {} - 请求的url - {}".format(proxy, request.url))
                return request

        elif "TimeoutError" in repr(exception):
            logger.info("下载超时,返回重新下载,url:{}".format(request.url))
            return request


class RandomProxyUserPwdMiddlerware(object):
    """
    带账号密码的代理IP
    """
    user_pwd_ip_list = [
            '139.198.4.42:444444',
    ]

    def process_request(self, request, spider):
        proxy = {'ip_port': random.choice(self.user_pwd_ip_list), 'user_pass': 'username:password'}
        if request.url.startswith('http://'):
            request.meta['proxy'] = "http://{}".format(proxy.get('ip_port'))
            encoded_user_pass = base64.b64encode(proxy.get('user_pass').encode('utf-8'))
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass.decode()
            logger.debug('http链接,ip:{}'.format(request.meta.get('proxy')))
        else:
            request.meta['proxy'] = "https://{}".format(proxy.get('ip_port'))
            encoded_user_pass = base64.b64encode(proxy.get('user_pass').encode('utf-8'))
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass.decode()
            logger.debug('https链接,ip:{}'.format(request.meta.get('proxy')))


class LocalRetryMiddlerware(RetryMiddleware):
    """
    重新定义重试中间件
    """
    redis_proxy_connection = redis.Redis(
        host=settings.REDIS_PROXIES_HOST,
        port=settings.REDIS_PROXIES_PORT,
        password=settings.REDIS_PROXIES_PASSWORD,
        db=settings.REDIS_PROXIES_DB,
    )
    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
    )

    def del_proxy(self, proxy):
        """
        删除代理
        """
        self.redis_proxy_connection.srem("proxies", proxy)

    def process_response(self, request, response, spider):

        if response.status in [302, 403]:
            proxy = request.meta.get("proxy")
            if proxy:
               proxy = proxy.split("//")[1]
               logger.info("{} - 响应码是302或者403删除代理 - {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), proxy))
               self.del_proxy(proxy)
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        if response.status == 404:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            # 全部重试错误，要保存错误的url和参数 - start
            error_request = settings.SPIDER_ERRROR_URLS
            self.redis_client.sadd(error_request, request.url)
            # 全部重试错误，要保存错误的url和参数 - en
            stats.inc_value('retry/max_reached')
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
