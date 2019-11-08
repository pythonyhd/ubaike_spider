# -*- coding: utf-8 -*-
# @Time    : 2019/9/24 13:05
# @Author  : Yasaka.Yu
# @File    : filter_fact.py
import hashlib
import time


def get_md5_value(_str):
    """
    MD5加密算法
    :param _str:
    :return:
    """
    if isinstance(_str, str):
        md5_obj = hashlib.md5()
        md5_obj.update(_str.encode())
        md5_code = md5_obj.hexdigest()
        return md5_code
    else:
        return None


def filter_base_data(item):
    """
    基本信息去重
    :param item:
    :return:
    """
    if isinstance(item, dict):
        xq_url = item.get('xq_url')
        oname = item.get('oname')
        cj_sj = str(time.time())

        if xq_url:
            if oname:
                if cj_sj:
                    _str = xq_url + oname + cj_sj
                    return get_md5_value(_str)
                else:
                    _str = xq_url + oname
                    return get_md5_value(_str)
            else:
                _str = xq_url
                return get_md5_value(_str)
        else:
            return None
    return None


def filter_gdinfo_data(item):
    """
    股东去重
    :param item:
    :return:
    """
    if isinstance(item, dict):
        gd_name = item.get('gd_name')
        gd_lx = item.get('gd_lx')
        cj_sj = str(time.time())
        oname = item.get('oname')
        rj_cze = item.get('rj_cze')
        cg_bl = item.get('cg_bl')

        if cj_sj:
            if oname:
                if gd_name:
                    if gd_lx:
                        if rj_cze:
                            if cg_bl:
                                _str = cj_sj + oname + gd_name + gd_lx + rj_cze + cg_bl
                                return get_md5_value(_str)
                            else:
                                _str = cj_sj + oname + gd_name + gd_lx + rj_cze
                                return get_md5_value(_str)
                        else:
                            _str = cj_sj + oname + gd_name + gd_lx
                            return get_md5_value(_str)
                    else:
                        _str = cj_sj + oname + gd_name
                        return get_md5_value(_str)
                else:
                    _str = cj_sj + oname
                    return get_md5_value(_str)
            else:
                _str = cj_sj
                return get_md5_value(_str)
        else:
            return None
    return None


def filter_main_people(item):
    """
    主要人员过滤
    :param item:
    :return:
    """
    if isinstance(item, dict):
        xq_url = item.get('xq_url')
        oname = item.get('oname')
        employee_name = item.get('employee_name')
        employee_job = item.get('employee_job')
        cj_sj = str(time.time())

        if xq_url:
            if oname:
                if employee_name:
                    if employee_job:
                        if cj_sj:
                            _str = xq_url + oname + employee_name + employee_job + cj_sj
                            return get_md5_value(_str)
                        else:
                            _str = xq_url + oname + employee_name + employee_job
                            return get_md5_value(_str)
                    else:
                        _str = xq_url + oname + employee_name
                        return get_md5_value(_str)
                else:
                    _str = xq_url + oname
                    return get_md5_value(_str)
            else:
                _str = xq_url
                return get_md5_value(_str)
        else:
            return None
    return None


def filter_change_data(item):
    """
    变更
    :param item:
    :return:
    """
    if isinstance(item, dict):
        xq_url = item.get('xq_url')
        oname = item.get('oname')
        cj_sj = str(time.time())

        if xq_url:
            if oname:
                if cj_sj:
                    _str = xq_url + oname + cj_sj
                    return get_md5_value(_str)
                else:
                    _str = xq_url + oname
                    return get_md5_value(_str)
            else:
                _str = xq_url
                return get_md5_value(_str)
        else:
            return None
    else:
        return None


def filter_jyyc_data(item):
    """
    经营异常去重
    :param item:
    :return:
    """
    if isinstance(item, dict):
        xq_url = item.get('xq_url')
        oname = item.get('oname')
        cf_jdrq = item.get('cf_jdrq')
        cf_xzjg = item.get('cf_xzjg')
        cj_sj = str(time.time())

        if xq_url:
            if oname:
                if cf_jdrq:
                    if cf_xzjg:
                        if cj_sj:
                            _str = xq_url + oname + cf_jdrq + cf_xzjg + cj_sj
                            return get_md5_value(_str)
                        else:
                            _str = xq_url + oname + cf_jdrq + cf_xzjg
                            return get_md5_value(_str)
                    else:
                        _str = xq_url + oname + cf_jdrq
                        return get_md5_value(_str)
                else:
                    _str = xq_url + oname
                    return get_md5_value(_str)
            else:
                _str = xq_url
                return get_md5_value(_str)
        else:
            return None
    else:
        return None


def filter_sxinfo_data(item):
    """
    失信去重规则
    :param item:
    :return:
    """
    if isinstance(item, dict):
        xq_url = item.get('xq_url')
        oname = item.get('oname')
        cf_wsh = item.get('cf_wsh')
        lian_sj = item.get('lian_sj')
        cj_sj = str(time.time())

        if xq_url:
            if oname:
                if cf_wsh:
                    if lian_sj:
                        if cj_sj:
                            _str = xq_url + oname + cf_wsh + lian_sj + cj_sj
                            return get_md5_value(_str)
                        else:
                            _str = xq_url + oname + cf_wsh + lian_sj
                            return get_md5_value(_str)
                    else:
                        _str = xq_url + oname + cf_wsh
                        return get_md5_value(_str)
                else:
                    _str = xq_url + oname
                    return get_md5_value(_str)
            else:
                _str = xq_url
                return get_md5_value(_str)
        else:
            return None
    return None


def filter_factory(item):
    sj_type = item.get('sj_type')
    if sj_type == 'base':
        return filter_base_data(item)
    elif sj_type == 'gdinfo':
        return filter_gdinfo_data(item)
    elif sj_type == 'main_people':
        return filter_main_people(item)
    elif sj_type == 'jyyc':
        return filter_jyyc_data(item)
    elif sj_type == 'sxinfo':
        return filter_sxinfo_data(item)
    elif sj_type == 'change':
        return filter_change_data(item)