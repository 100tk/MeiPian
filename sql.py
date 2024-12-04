from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData

# 创建数据库引擎
engine = create_engine("sqlite:///meipian.db", echo=True)
metdata = MetaData()
# 创建一个数据表
users = Table(
    "users",
    metdata,
    Column("user_id", Integer),
    Column("mask_id", String, primary_key=True),
    Column("age", Integer),
)

metdata.create_all(engine)
