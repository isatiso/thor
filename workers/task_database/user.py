# coding:utf-8
from models.model import User
from workers.manager import APP as app, Tasks, exc_handler
from sqlalchemy_filters import apply_sort, apply_filters, apply_pagination


@app.task
@exc_handler
def query_account(options=None, **kwargs):
    """Query account info."""
    sess = kwargs.get('sess')

    email = kwargs.get('email')
    user_id = kwargs.get('user_id')

    account = sess.query(User)
    print(options)
    if user_id:
        account = account.filter(User.user_id == user_id)
    elif email:
        account = account.filter(User.email == email)
    else:
        return None

    account = account.first()

    if account:
        result = account.to_dict(options)
    else:
        result = None
    return result


@app.task
@exc_handler
def query_account_pagination(options=None, page_number=1, page_size=20, **kwargs):
    """Query account info."""
    sess = kwargs.get('sess')
    filter_spec = kwargs.get('filter_spec', [])
    sort_spec = kwargs.get('sort_spec', [])

    account = sess.query(User)

    account = apply_filters(account, filter_spec)
    account = apply_sort(account, sort_spec)

    account, pagination = apply_pagination(
        account, page_number=page_number, page_size=page_size)

    if account:
        # result = account.to_dict(options)
        result = [_account.to_dict(options) for _account in account]
    else:
        result = None
    return result, pagination


@app.task
@exc_handler
def insert_account(
    user_id,
    email,
    password,
    first_name,
    last_name,
    register_time,
    permission=1,
    company=None,
    title=None,
    country=None,
    avatar=None,
    register_ip='0.0.0.0',
    industry='',
    login_inc=0,
    expire_time=0,
        **kwargs):
    """Insert an account."""

    print(expire_time)
    sess = kwargs.get('sess')
    new_account = User(
        user_id=user_id,
        email=email,
        password=password,
        register_time=register_time,
        permission=permission,
        first_name=first_name,
        last_name=last_name,
        company=company,
        title=title,
        country=country,
        avatar=avatar,
        login_inc=login_inc,
        register_ip=register_ip,
        industry=industry,
        expire_time=expire_time
    )
    print(new_account.to_dict())
    sess.add(new_account)
    sess.commit()

    return dict(status=0, msg='Successfully')


@app.task
@exc_handler
def update_account_expire_time(user_id, expire_time, **kwargs):
    """Update expire time of an account."""
    sess = kwargs.get('sess')
    account = sess.query(User).filter(User.user_id == user_id).update({
        User.expire_time:
        expire_time
    })
    result = account
    sess.commit()
    return result


@app.task
@exc_handler
def update_account_permission(user_id, permission, **kwargs):
    """Update expire time of an account."""
    sess = kwargs.get('sess')
    account = sess.query(User).filter(User.user_id == user_id).update({
        User.permission:
        permission
    })
    result = account
    sess.commit()
    return result


@app.task
@exc_handler
def update_account_info(**kwargs):
    """Update info of an account."""
    sess = kwargs.get('sess')
    user_id = kwargs.get('user_id')
    email = kwargs.get('email')
    if not user_id and not email:
        return dict(
            result=0,
            status=1,
            msg=('Missing Argument, '
                 'either "user_id" or "email" should in arguments.'),
            data=None
        )
    invert_dict = dict(
        first_name=User.first_name,
        last_name=User.last_name,
        company=User.company,
        title=User.title,
        country=User.country,
        avatar=User.avatar,
        industry=User.industry,
    )

    key_list = list(invert_dict.keys())
    for key in key_list:
        if key not in kwargs:
            del invert_dict[key]

    update_dict = dict([(invert_dict[k], kwargs[k]) for k in invert_dict])

    if update_dict:
        account = sess.query(User)
        if user_id:
            account = account.filter(
                User.user_id == user_id).update(update_dict)
        elif email:
            account = account.filter(
                User.email == email).update(update_dict)
        else:
            return dict(
                result=0,
                status=2,
                msg=('Missing Argument, '
                     'either "user_id" or "email" should in arguments.'),
                data=None
            )
        result = account
        sess.commit()
        res = dict(status=0, msg='Successfully', update=result)
    else:
        res = dict(status=3, msg='Failure')

    return res


@app.task
@exc_handler
def update_account_login_inc(user_id, **kwargs):
    """Update total pages of a file."""
    sess = kwargs.get('sess')
    account = sess.query(User).filter(User.user_id == user_id).update({
        User.login_inc:
        User.login_inc+1
    })
    result = account
    sess.commit()
    return dict(status=0, msg='Successfully')


@app.task
@exc_handler
def update_account_password(user_id, **kwargs):
    """Update total pages of a file."""
    sess = kwargs.get('sess')
    password = kwargs.get('password')
    account = sess.query(User).filter(User.user_id == user_id).update({
        User.password:
        password
    })
    result = account
    sess.commit()
    return dict(status=0, msg='Successfully')


@app.task
@exc_handler
def update_account_email(user_id, email, old_email, **kwargs):
    """Update email of an account."""
    sess = kwargs.get('sess')
    account = sess.query(User).filter(User.user_id == user_id).filter(User.email == old_email).update({
        User.email:
        email
    })
    result = account
    sess.commit()
    return result


TASK_DICT = [
    query_account_pagination,
    query_account,
    insert_account,
    update_account_expire_time,
    update_account_permission,
    update_account_info,
    update_account_login_inc,
    update_account_password,
    update_account_email,
]
