# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
import re
from copy import deepcopy
from ubaike_project.work_utils.handle_data import deal_with_data
import logging
logger = logging.getLogger(__name__)


class UbaikeSpider(scrapy.Spider):
    name = 'ubaike'
    allowed_domains = ['ubaike.cn']
    start_urls = ['https://www.ubaike.cn/']

    def get_headers(self, referer_url):
        if referer_url:
            headers = {
                'referer': referer_url,
            }
        else:
            headers = {
                'referer': referer_url,
            }
        return headers

    def parse(self, response):
        list_url_info = response.xpath('//div[starts-with(@class,"line")]//a/@href').getall()
        for url in list_url_info:
            yield scrapy.Request(
                url=url,
                callback=self.get_list_info,
            )

    def get_list_info(self, response):
        """
        翻页跟解析
        :param response:
        :return:
        """
        # todo 提取下一页的链接
        next_url = response.xpath('//a[contains(text(),"下一页")]/@href').get()
        next_url = urljoin(response.url, next_url)
        if next_url:
            yield scrapy.Request(
                url=next_url,
                callback=self.get_list_info,
                dont_filter=True,
                priority=2,
                headers=self.get_headers(response.url),
            )
        else:
            logger.info('该地区翻页结束,总页数:{}'.format(response.url))

        # todo 提取列表页到详情页公司链接
        index_url_list = response.xpath('//div[@class="content"]/a/@href').extract()
        if index_url_list:
            for url in index_url_list:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_details,
                    priority=3,
                )
        else:
            logger.info("提取详情页url失败")

    def parse_details(self, response):
        """
        解析数据
        :param response:
        :return:
        """
        # todo 解析基本信息存MySQL
        selector = scrapy.Selector(text=response.text)
        telephone = selector.xpath('//span[contains(text(),"联系电话")]/text()').re_first(r'：(.+)')  # 电话
        email = selector.xpath('//p[contains(text(),"邮箱")]/text()').re_first(r'：(.+)')  # 邮箱
        basic_items = selector.xpath('//div[starts-with(@class,"basic-item")]/div[last()]//text()').getall()
        if email:
            keys = ['oname', 'regcode', 'uccode', 'zc_zb', 'cl_rq', 'qy_lx', 'jy_fw', 'cf_r_dz', 'ye_qx', 'regstate_cn']
            item = dict(zip(keys, basic_items))
            item['pname'] = selector.xpath('//div[contains(text(),"法")]/following-sibling::div[1]/text()').get()
        else:
            keys = ['oname', 'pname', 'regcode', 'uccode', 'zc_zb', 'cl_rq', 'qy_lx', 'jy_fw', 'cf_r_dz', 'ye_qx', 'regstate_cn']
            item = dict(zip(keys, basic_items))
        update_time = re.search(r'\"upDate\": \"(.*?)\"', response.text)
        if update_time:
            update_time = update_time.group(1)[:10]
        else:
            update_time = ""
        item['fb_rq'] = update_time
        item['telephone'] = telephone
        item['email'] = email
        item['dq_mc'] = selector.xpath('//a[@data-original-title="所属城市"]//text()').extract_first('')
        item['xq_url'] = response.url
        item['sj_type'] = 'base'
        item['xxly'] = '红盾查询'
        if item['oname']:
            item['oname'] = item['oname']
        else:
            item['oname'] = selector.xpath('//h1[@class="title"]/text()').get()
        yield item

        # todo 解析股东信息存MySQL
        item_gdinfo = {}
        other_gd = selector.xpath('//div[contains(text(),"股东信息")]/following-sibling::div[1]/span/text()').get()
        if other_gd == '无':  # 判断是否有股东信息
            logger.debug('无股东信息')
        else:
            item_gdinfo['oname'] = item['oname']
            item_gdinfo['sj_type'] = 'gdinfo'
            item_gdinfo['xq_url'] = item['xq_url']
            item['xxly'] = '红盾查询'
            base_gdinfos = selector.xpath('//div[@class="stock-item"]')
            for gd_data in base_gdinfos:
                gd_name = gd_data.xpath('./div[@class="stock-title"]/span/text()').get('')
                cg_bl = gd_data.xpath('.//div[@class="stock-content"]/div[1]/div[1]/div[2]/text()').get()
                gd_lx = gd_data.xpath('.//div[contains(text(),"股东类型")]/following-sibling::div[1]/text()').get()
                rj_cze = gd_data.xpath('.//div[contains(text(),"认缴出资额")]/following-sibling::div[1]/text()').get()
                if rj_cze:
                    item_gdinfo['rj_cze'] = deal_with_data(rj_cze) + '万元'
                else:
                    item_gdinfo['rj_cze'] = ''
                rj_czrq = gd_data.xpath('.//div[contains(text(),"认缴出资日期")]/following-sibling::div[1]/text()').get()
                if gd_name:
                    item_gdinfo['gd_name'] = gd_name.strip()
                else:
                    item_gdinfo['gd_name'] = ''
                item_gdinfo['gd_lx'] = deal_with_data(gd_lx)
                item_gdinfo['rj_czrq'] = deal_with_data(rj_czrq)
                item_gdinfo['cg_bl'] = cg_bl
                yield item_gdinfo
        # todo 解析主要人员信息存MySQL
        item_main_people = {}
        wother_main = selector.xpath('//div[contains(text(),"主要人员")]/following-sibling::div[1]/span/text()').get()
        if wother_main == '无':
            logger.debug('无主要人员信息')
            # return None
        else:
            item_main_people['oname'] = item['oname']
            item_main_people['sj_type'] = 'main_people'
            item_main_people['xq_url'] = item['xq_url']
            item['xxly'] = '红盾查询'
            main_people_data = selector.xpath('//div[contains(text(),"主要人员")]/following-sibling::div[1]/div/div/div')
            for main_people in main_people_data:
                employee_name = main_people.xpath('./div[1]//text()').get('')
                employee_job = main_people.xpath('./div[2]//text()').get('')
                item_main_people['employee_name'] = employee_name
                item_main_people['employee_job'] = employee_job
                yield item_main_people
        # todo 解析变更信息存MySQL
        item_change = {}
        other_change = selector.xpath('//div[contains(text(),"变更")]/following-sibling::div[1]/span/text()').get()
        if other_change == '无':
            logger.debug('无变更')
            # return None
        else:
            item_change['oname'] = item['oname']
            item_change['sj_type'] = 'change'
            item_change['xq_url'] = item['xq_url']
            item['xxly'] = '红盾查询'
            ws_nr_txt_list = selector.xpath('//div[@class="change-wrap"]').getall()
            item_change['ws_nr_txt'] = str(ws_nr_txt_list)
            change_base = selector.xpath('//div[@class="change-item"]')
            for change_data in change_base:
                item_change['change_title'] = change_data.xpath('./div[@class="change-date"]/text()').get()  # 变更名称
                yield item_change

        # todo 解析经营异常信息存MySQL
        item_jyyc = {}
        jyyc_data = selector.xpath('//div[contains(text(),"经营异常")]/following-sibling::div[1]/div/table/tbody/tr')
        if jyyc_data:
            item_jyyc['oname'] = item['oname']
            item_jyyc['pname'] = item['pname']
            item_jyyc['uccode'] = item['uccode']
            item_jyyc['regcode'] = item['regcode']
            item_jyyc['cf_r_dz'] = item['cf_r_dz']
            item_jyyc['regstate_cn'] = item['regstate_cn']
            item_jyyc['dq_mc'] = item['dq_mc']
            item_jyyc['sj_type'] = 'jyyc'
            item_jyyc['xq_url'] = item['xq_url']
            item['site_id'] = 28387
            item['xxly'] = '红盾网-经营异常信息'
            for jyyc in jyyc_data:
                item_jyyc['cf_jdrq'] = jyyc.xpath('./td[1]//text()').extract_first('')
                item_jyyc['cf_sy'] = jyyc.xpath('./td[2]//text()').extract_first('')
                item_jyyc['cf_xzjg'] = jyyc.xpath('./td[3]//text()').extract_first('')
                yield item_jyyc
        # todo 获取失信被执行人url
        sxbzxr_url = selector.xpath('//div[contains(text(),"失信被执行人")]/following-sibling::div[1]//table//a/@href').getall()
        if sxbzxr_url:
            for link in sxbzxr_url:
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_index,
                    priority=3,
                    meta={'item': deepcopy(item)},
                )
        else:
            logger.debug("没有失信被执行人信息")

    def parse_index(self,response):
        sxinfo_item = {}
        item_base_info = response.meta.get("item")
        uccode = item_base_info.get("uccode")
        pname = item_base_info.get("pname")
        sxinfo_item['uccode'] = uccode
        sxinfo_item['pname'] = pname
        sxinfo_item['wbbz'] = '失信被执行人名单'
        sxinfo_item['xxly'] = '红盾网-失信被执行人信息'
        sxinfo_item['xq_url'] = response.url
        sxinfo_item['sj_type'] = 'sxinfo'
        sxinfo_item['site_id'] = 28388
        selector = scrapy.Selector(text=response.text)
        base_data_info = selector.xpath('//div[@class="r_base"]/table[1]')
        for data in base_data_info:
            sxinfo_item['oname'] = data.xpath('./tr[1]/td[2]/div/a//text()').extract_first('')
            sxinfo_item['etcode'] = data.xpath('./tr[2]/td[2]/div//text()').extract_first('')
            sxinfo_item['zxwh'] = data.xpath('./tr[3]/td[2]/div//text()').extract_first('')
            sxinfo_item['cf_wsh'] = data.xpath('./tr[4]/td[2]/div//text()').extract_first('')
            sxinfo_item['cf_xzjg'] = data.xpath('./tr[5]/td[2]/div//text()').extract_first('')
            sxinfo_item['yiwu'] = data.xpath('./tr[6]/td[2]/div//text()').extract_first('')
            sxinfo_item['lvxingqk'] = data.xpath('./tr[7]/td[2]/div//text()').extract_first('')
            sxinfo_item['zxfy'] = data.xpath('./tr[8]/td[2]/div//text()').extract_first('')
            sxinfo_item['sf'] = data.xpath('./tr[9]/td[2]/div//text()').extract_first('')
            sxinfo_item['lian_sj'] = data.xpath('./tr[10]/td[2]/div//text()').extract_first('')
            sxinfo_item['fb_rq'] = data.xpath('./tr[11]/td[2]/div//text()').extract_first('')
            sxinfo_item['qingxing'] = data.xpath('./tr[12]/td[2]/div//text()').extract_first('')
            yield sxinfo_item