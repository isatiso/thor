from test import test_dec, get_sess
import time
import enum
import asyncio
from datetime import datetime
from pprint import pprint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (create_engine, Table, Column, Integer, String,
                        MetaData, TIMESTAMP, SmallInteger, CHAR)
from sqlalchemy.sql import select
from sqlalchemy.orm import Query

from sqlalchemy import PrimaryKeyConstraint

Base = declarative_base()


class Addition:

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP  ON UPDATE CURRENT_TIMESTAMP'))

    def to_dict(self, *options, **alias):
        res = dict()
        for key in options:
            alias[key] = None

        for key in self.__dict__:
            if not alias or key in alias:
                if not key.startswith('_'):
                    if isinstance(alias.get(key), str):
                        real_key = alias[key]
                    else:
                        real_key = key
                    if isinstance(self.__dict__[key], enum.Enum):
                        res[real_key] = self.__dict__[key].name
                    elif isinstance(self.__dict__[key], datetime):
                        res[real_key] = int(self.__dict__[key].timestamp())
                    else:
                        res[real_key] = self.__dict__[key]

        return res


class User(Base, Addition):
    """User Model."""
    __tablename__ = 'user'

    user_id = Column(Integer)
    mail = Column(String(120), index=True)
    phone = Column(String(20), index=True)
    username = Column(String(10), index=True)
    password = Column(CHAR(32))

    is_super = Column(SmallInteger, server_default=text('0'))
    active = Column(SmallInteger, server_default=text('0'))

    __table_args__ = (
        PrimaryKeyConstraint('user_id'),
        {
            'mysql_engine': 'InnoDB'
        },
    )


def main():
    # a = add(1, 2, test_sess='poiuoi')

    # print(a)
    # pprint(globals())

    eng = create_engine('sqlite:///test.db')

    DB_ENGINE = create_engine(
        # 'mysql+pymysql://plank:ridiculous@dev.machine:3306/lazor?charset=utf8',
        'sqlite:///test.db',
        echo=False,
        pool_recycle=100,
        encoding='utf-8')

    SESS = sessionmaker()

    sess = SESS(bind=DB_ENGINE)
    print(type(sess))

    print('sess', sess)

    # # sess.add(User(username='1111111111'))
    # query = Query([User])

    # user_list = query.limit(2)
    # query.session = sess
    # for user in user_list:
    #     print(user.to_dict())

    # sess.bind = DB_ENGINE
    # sess.commit()

    # with eng.connect() as con:

    #     meta = MetaData(eng)
    #     cars = Table('Cars', meta,
    #         Column('Id', Integer, primary_key=True),
    #         Column('Name', String),
    #         Column('Price', Integer)
    #     )

    #     stm = select([cars.c.Name, cars.c.Price]).limit(3)
    #     print(stm)


if __name__ == "__main__":
    main()
    # print(add.__doc__)
    # print(dir(add))
    # loop = asyncio.get_event_loop()
    # # Blocking call which returns when the display_date() coroutine is done
    # loop.run_until_complete(main())
    # print(dir(loop))
    # loop.close()