from test import test_dec, get_sess
import time

import asyncio
from pprint import pprint

from sqlalchemy import (create_engine, Table, Column, Integer, 
    String, MetaData)
from sqlalchemy.sql import select

@test_dec
def add(x, y, **kwargs):
    """test add doc."""
    # global sess
    # sess = get_sess()
    # print(sess)
    print('add', add.__dict__)
    return x + y


def main():
    # a = add(1, 2, test_sess='poiuoi')

    # print(a)
    # pprint(globals())

    eng = create_engine('sqlite:///test.db')

    with eng.connect() as con:

        meta = MetaData(eng)
        cars = Table('Cars', meta,
            Column('Id', Integer, primary_key=True),
            Column('Name', String),
            Column('Price', Integer)
        )

        stm = select([cars.c.Name, cars.c.Price]).limit(3)
        print(stm)



if __name__ == "__main__":
    main()
    # print(add.__doc__)
    # print(dir(add))
    # loop = asyncio.get_event_loop()
    # # Blocking call which returns when the display_date() coroutine is done
    # loop.run_until_complete(main())
    # print(dir(loop))
    # loop.close()