# -*- coding: utf-8 -*-
# @Time    : 2019/9/25 9:17
# @Author  : Yasaka.Yu
# @File    : creat_mysql_data.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ubaike_project.settings import DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_NAME,DB_CHARSET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,TEXT,DATETIME,SMALLINT,ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
import warnings
# from sqlalchemy_utils import database_exists, create_database


warnings.filterwarnings("ignore")
# 初始化数据库连接:
engine = create_engine(
    "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset={charset}".format(username=DB_USER,password=DB_PASSWORD,host=DB_HOST,port=DB_PORT,db=DB_NAME,charset=DB_CHARSET),
    # echo=True,  # 打印过程
    # max_overflow=0,  # 超过连接池大小外最多创建的连接
    # pool_size=5,  # 连接池大小
    # pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    # pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收(重置)
)
# if not database_exists(engine.url):
#     create_database(engine.url)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
# 创建对象的基类:
Base = declarative_base()


class HdBaseInfo(Base):
    """
    企业基本信息表
    """
    __tablename__ = 'hd_base_info'
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    ws_pc_id = Column(String(length=32), nullable=False, unique=True, comment='MD5排重字段')
    oname = Column(String(length=64), nullable=True, index=True, comment='主体名称')
    pname = Column(String(length=16), nullable=True, comment='法人')
    regcode = Column(String(length=32), nullable=True, comment='注册号')
    uccode = Column(String(length=32), nullable=True, comment='统一代码或身份证')
    zc_zb = Column(String(length=64), nullable=True, comment='注册资本')
    cl_rq = Column(String(length=12), nullable=True, comment='成立日期')
    qy_lx = Column(String(length=32), nullable=True, comment='企业类型')
    jy_fw = Column(TEXT, nullable=True, comment='经营范围')
    cf_r_dz = Column(String(length=128), nullable=True, comment='地址')
    ye_qx = Column(String(length=32), nullable=True, comment='营业期限')
    regstate_cn = Column(String(length=16), nullable=True, comment='经营状态')
    fb_rq = Column(String(length=16), nullable=True, comment='发布日期')
    telephone = Column(String(length=32), nullable=True, comment='电话')
    email = Column(String(length=16), nullable=True, comment='邮箱')
    dq_mc = Column(String(length=16), nullable=True, comment='地区名')
    xq_url = Column(String(length=64), nullable=True, comment='详情链接')
    xxly = Column(String(length=6), nullable=True, comment='信息来源')
    cj_sj = Column(DATETIME, default=datetime.now, nullable=False, comment='采集时间')
    bz = Column(String(length=8), nullable=True, comment='备注')
    sj_type = Column(String(length=12), nullable=True, comment='类型')
    zt = Column(SMALLINT, nullable=True, default=0)
    zt1 = Column(SMALLINT, nullable=True, default=0)
    zt2 = Column(SMALLINT, nullable=True, default=0)
    zt3 = Column(SMALLINT, nullable=True, default=0)

    # 与生成表结构无关，仅用于查询方便，创建外键关系
    # gd_infos = relationship("HdGdInfo", backref='baseinfo')  # backref 反向查询
    # major_infos = relationship('HdmainPeople', backref='baseinfo')
    # change_infos = relationship('HdChanges', backref='baseinfo')

    def __repr__(self):
        return '<HdBaseInfo:- {} ->'.format(self.oname)


class HdGdInfo(Base):
    """
    红盾网股东表
    """
    __tablename__ = 'hd_gd_info'
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    ws_pc_id = Column(String(length=32), nullable=False, unique=True, comment='MD5排重字段')
    # 跟基本信息表外键关联
    # oname = Column(String(length=64), ForeignKey('hd_base_info.oname'), nullable=True, index=True, comment='主体名称')
    oname = Column(String(length=64), nullable=True, index=True, comment='主体名称')
    gd_name = Column(String(length=32), nullable=True, comment='股东姓名')
    gd_lx = Column(String(length=16), nullable=True, comment='股东类型')
    rj_cze = Column(String(length=16), nullable=True, comment='认缴出资额')
    rj_czrq = Column(String(length=64), nullable=True, comment='认缴出资日期')
    cg_bl = Column(String(length=16), nullable=True, comment='持股比例')
    xq_url = Column(String(length=64), nullable=True, comment='详情链接')
    xxly = Column(String(length=6), nullable=True, comment='信息来源')
    cj_sj = Column(DATETIME, default=datetime.now, nullable=False, comment='采集时间')
    bz = Column(String(length=8), nullable=True, comment='备注')
    sj_type = Column(String(length=12), nullable=True, comment='类型')
    zt = Column(SMALLINT, nullable=True, default=0)
    zt1 = Column(SMALLINT, nullable=True, default=0)
    zt2 = Column(SMALLINT, nullable=True, default=0)
    zt3 = Column(SMALLINT, nullable=True, default=0)

    def __repr__(self):
        return '<HdGdInfo:- {} ->'.format(self.oname)


class HdmainPeople(Base):
    """
    红盾网主要人员
    """
    __tablename__ = 'hd_major_info'
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    ws_pc_id = Column(String(length=32), nullable=False, unique=True, comment='MD5排重字段')
    # 跟基本信息表外键关联
    # oname = Column(String(length=64), ForeignKey('hd_base_info.oname'), nullable=True, index=True, comment='主体名称')
    oname = Column(String(length=64), nullable=True, index=True, comment='主体名称')
    xq_url = Column(String(length=64), nullable=True, comment='详情链接')
    employee_name = Column(String(length=16), nullable=True, comment='主要人员姓名')
    employee_job = Column(String(length=16), nullable=True, comment='主要人员职位')
    xxly = Column(String(length=6), nullable=True, comment='信息来源')
    cj_sj = Column(DATETIME, default=datetime.now, nullable=False, comment='采集时间')
    bz = Column(String(length=8), nullable=True, comment='备注')
    sj_type = Column(String(length=12), nullable=True, comment='类型')
    zt = Column(SMALLINT, nullable=True, default=0)
    zt1 = Column(SMALLINT, nullable=True, default=0)
    zt2 = Column(SMALLINT, nullable=True, default=0)
    zt3 = Column(SMALLINT, nullable=True, default=0)

    def __repr__(self):
        return '<HdmainPeople:- {} ->'.format(self.oname)


class HdChanges(Base):
    """
    红盾网变更信息
    """
    __tablename__ = 'hd_change_info'
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    ws_pc_id = Column(String(length=32), nullable=False, unique=True, comment='MD5排重字段')
    # 跟基本信息表外键关联
    # oname = Column(String(length=64), ForeignKey('hd_base_info.oname'), nullable=True, index=True, comment='主体名称')
    oname = Column(String(length=64), nullable=True, index=True, comment='主体名称')
    xq_url = Column(String(length=64), nullable=True, comment='详情链接')
    ws_nr_txt = Column(TEXT, nullable=True, comment='变更内容')
    change_title = Column(String(length=64), nullable=True, comment='变更标题')
    xxly = Column(String(length=6), nullable=True, comment='信息来源')
    cj_sj = Column(DATETIME, default=datetime.now, nullable=False, comment='采集时间')
    bz = Column(String(length=8), nullable=True, comment='备注')
    sj_type = Column(String(length=12), nullable=True, comment='类型')
    zt = Column(SMALLINT, nullable=True, default=0)
    zt1 = Column(SMALLINT, nullable=True, default=0)
    zt2 = Column(SMALLINT, nullable=True, default=0)
    zt3 = Column(SMALLINT, nullable=True, default=0)

    def __repr__(self):
        return '<HdChanges:- {} ->'.format(self.oname)


class HdJyyc(Base):
    """
    红盾网经营异常
    """
    __tablename__ = 'hd_jyyc_info'

    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    ws_pc_id = Column(String(length=32), nullable=False, unique=True, comment='MD5排重字段')
    oname = Column(String(length=64), nullable=True, index=True, comment='主体名称')
    pname = Column(String(length=10), nullable=True, comment='法人')
    regcode = Column(String(length=32), nullable=True, comment='注册号')
    uccode = Column(String(length=32), nullable=True, comment='统一代码或身份证')
    regstate_cn = Column(String(length=16), nullable=True, comment='经营状态')
    cf_r_dz = Column(String(length=128), nullable=True, comment='地址')
    dq_mc = Column(String(length=16), nullable=True, comment='地区名')
    cf_sy = Column(String(length=64), nullable=True, comment='事由')
    cf_xzjg = Column(String(length=128), nullable=True, comment='处罚机关')
    cf_jdrq = Column(String(length=64), nullable=True, comment='处罚决定日期')
    xq_url = Column(String(length=64), nullable=True, comment='详情链接')
    xxly = Column(String(length=6), nullable=True, comment='信息来源')
    site_id = Column(Integer, nullable=True, comment='任务id')
    cj_sj = Column(DATETIME, default=datetime.now, nullable=False, comment='采集时间')
    bz = Column(String(length=8), nullable=True, comment='备注')
    sj_type = Column(String(length=12), nullable=True, comment='类型')
    zt = Column(SMALLINT, nullable=True, default=0)
    zt1 = Column(SMALLINT, nullable=True, default=0)
    zt2 = Column(SMALLINT, nullable=True, default=0)
    zt3 = Column(SMALLINT, nullable=True, default=0)

    def __repr__(self):
        return "<HdJyyc %r>" % self.oname


class HdSxBzxr(Base):
    """
    红盾网失信被执行人
    """

    __tablename__ = "hd_sxbzxr_info"
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    ws_pc_id = Column(String(length=32), nullable=False, unique=True, comment='MD5排重字段')
    oname = Column(String(length=64), nullable=True, index=True, comment='主体名称')
    pname = Column(String(length=10), nullable=True, comment='法人')
    uccode = Column(String(length=32), nullable=True, comment='统一代码或身份证')
    etcode = Column(String(length=32), nullable=True, comment='身份证号／组织机构代码')
    cf_wsh = Column(String(length=64), nullable=True, comment='案号')
    zxwh = Column(String(length=64), nullable=True, comment='执行依据文号')
    cf_xzjg = Column(String(length=64), nullable=True, comment='做出执行依据单位')
    fb_rq = Column(String(length=64), nullable=True, comment='发布日期')
    zxfy = Column(String(length=64), nullable=True, comment='执行法院')
    sf = Column(String(length=16), nullable=True, comment='省份')
    lian_sj = Column(String(length=16), nullable=True, comment='立案日期')
    yiwu = Column(TEXT, nullable=True, comment='义务')
    lvxingqk = Column(String(length=256), nullable=True, comment='履行情况')
    qingxing = Column(String(length=256), nullable=True, comment='具体情形')
    xq_url = Column(String(length=64), nullable=True, comment='详情链接')
    xxly = Column(String(length=15), nullable=True, comment='信息来源')
    site_id = Column(Integer, nullable=True, comment='任务id')
    cj_sj = Column(DATETIME, default=datetime.now, nullable=False, comment='采集时间')
    bz = Column(String(length=8), nullable=True, comment='备注')
    wbbz = Column(String(length=10), nullable=True, comment='外部备注')
    sj_type = Column(String(length=12), nullable=True, comment='类型')
    zt = Column(SMALLINT, nullable=True, default=0)
    zt1 = Column(SMALLINT, nullable=True, default=0)
    zt2 = Column(SMALLINT, nullable=True, default=0)
    zt3 = Column(SMALLINT, nullable=True, default=0)

    def __repr__(self):
        return "<HdSxBzxr %r>" % self.oname


if __name__ == '__main__':
    Base.metadata.create_all(engine)  # 新建表
    # Base.metadata.drop_all(engine)  # 删除表