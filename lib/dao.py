# coding:utf-8
from functools import wraps
import traceback
import enum
from datetime import datetime
from sqlalchemy import create_engine, exc as sqlexc
from sqlalchemy.orm import sessionmaker

from lib.utils.logger import dump_in, dump_out, dump_error
from config import CFG as O_O, _ENV as env

DB_ENGINE = create_engine(
    O_O.database.mysql, echo=False, pool_recycle=1000, encoding='utf-8')

SESS = sessionmaker(bind=DB_ENGINE)


def dict_of(entity, *options, **alias):
    res = dict()
    for key in options:
        alias[key] = None

    for key in entity.__dict__:
        if not alias or key in alias:
            if not key.startswith('_'):
                if isinstance(alias.get(key), str):
                    real_key = alias[key]
                else:
                    real_key = key
                if isinstance(entity.__dict__[key], enum.Enum):
                    res[real_key] = entity.__dict__[key].name
                elif isinstance(entity.__dict__[key], datetime):
                    res[real_key] = int(entity.__dict__[key].timestamp())
                else:
                    res[real_key] = entity.__dict__[key]

    return res


def transaction(function, rollback=True):
    """Wrap a handle shell to a query function."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Function that wrapped."""
        session = SESS()
        try:
            res = function(sess=session, *args, **kwargs)
        except sqlexc.IntegrityError as exception:
            res = dict(status=1, msg=str(exception.orig))
        except sqlexc.ProgrammingError as exception:
            res = dict(status=2, msg=str(exception.orig))
        except sqlexc.ResourceClosedError as exception:
            res = dict(status=3, msg=str(exception))
        except sqlexc.OperationalError as exception:
            res = dict(status=4, msg=str(exception.orig))
        except UnicodeEncodeError as exception:
            res = dict(status=5, msg=str(exception))
        except:
            dump_error('my exception\n', traceback.format_exc())
            res = dict(status=255, msg='Unknown Error.')
        finally:
            session.close()

        if res and 'status' in res:
            return res
        else:
            return dict(status=0, data=res)

    return wrapper