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
            'http': 'http://{}'.format(ip_port.decode('utf-8')),
            'https': 'https://{}'.format(ip_port.decode('utf-8')),
        }
        if request.url.startswith('http://'):
            request.meta['proxy'] = proxies.get('http')
            # logger.debug('http链接,ip:{}'.format(request.meta.get('proxy')))
        else:
            request.meta['proxy'] = proxies.get('https')
            # logger.debug('https链接,ip:{}'.format(request.meta.get('proxy')))

    def process_response(self, request, response, spider):
        if response.url == 'https://www.ubaike.cn/book.html':
            return request
        return response


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

    def delete_proxy(self, proxy):
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
               self.delete_proxy(proxy)
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
            error_request = spider.name + 'error_urls'
            self.redis_client.sadd(error_request, request.url)
            # 全部重试错误，要保存错误的url和参数 - en
            stats.inc_value('retry/max_reached')
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})

    def process_exception(self, request, exception, spider):
        if "ConnectionRefusedError" in repr(exception):
            proxy_spider = request.meta.get('proxy')
            proxy_redis = proxy_spider.split("//")[1]
            self.delete_proxy(proxy_redis)
            logger.info('目标计算机积极拒绝，删除代理-{}-请求url-{}-重新请求'.format(proxy_redis, request.url))
            return request

        elif "TCPTimedOutError" in repr(exception):
            logger.debug('连接方在一段时间后没有正确答复或连接的主机没有反应')
            return request

        elif "ConnectionError" in repr(exception):
            logger.debug("连接出错，无网络")
            return request

        elif "TimeoutError" in repr(exception):
            logger.debug('请求超时-请求url-{}-重新请求'.format(request.url))
            return request

        elif "ConnectionResetError" in repr(exception):
            logger.debug('远程主机强迫关闭了一个现有的连接')
            return request

        elif "ResponseNeverReceived" in repr(exception):
            return request
        else:
            logger.error('出现其他异常:{}--等待处理'.format(repr(exception)))