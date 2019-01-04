from test import test_dec, get_sess
import time

import asyncio
from pprint import pprint

from sqlalchemy.orm import sessionmaker
from sqlalchemy import (create_engine, Table, Column, Integer, String,
                        MetaData)
from sqlalchemy.sql import select
from sqlalchemy.orm import Query

from model.models import User


def main():
    # a = add(1, 2, test_sess='poiuoi')

    # print(a)
    # pprint(globals())

    eng = create_engine('sqlite:///test.db')

    DB_ENGINE = create_engine(
        'mysql+pymysql://plank:ridiculous@dev.machine:3306/lazor?charset=utf8',
        echo=False,
        pool_recycle=100,
        encoding='utf-8')

    SESS = sessionmaker()

    sess = SESS(bind=DB_ENGINE)

    print('sess', sess)

    # sess.add(User(username='1111111111'))
    query = Query([User])
    query.session = sess
    user_list = query.all()
    for user in user_list:
        print(user.to_dict())

    

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