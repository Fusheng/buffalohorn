from google.appengine.ext import db


def getAllAccounts():
    q = Account.all()
    results = q.fetch(1000)
    return results


def getAccountByEmail(email):
    q = Account.all()
    q.filter('email', email)
    results = q.fetch(1)
    if results:
        return results[0]
    else:
        return None


def genAccountId():
    q = db.GqlQuery("SELECT * FROM IdGen WHERE name = :1 ",
                    'account_id')
    result = q.fetch(1)
    if len(result) == 0:
        idGen = IdGen(name='account_id', value=1)
        idGen.put()
        return 1
    else:
        account = result[0]
        account.value = account.value + 1
        account.put()
        return account.value


def delAccount(accountId):
    q = db.GqlQuery("SELECT * FROM Account WHERE account_id = :1 ",
                    accountId)
    results = q.fetch(1000)
    for result in results:
        result.delete()


def get_sys_param_by_key(param_key):
    q = SysParams.all()
    q.filter('param_key', param_key)
    results = q.fetch(1)
    if results:
        return results[0]
    else:
        return None


class SysParams(db.Model):
    param_key = db.StringProperty(required=True)
    value = db.StringProperty(required=True)
    category = db.StringProperty(required=True)
    description = db.StringProperty()


class Account(db.Model):
    account_id = db.IntegerProperty(required=True)
    email = db.StringProperty(required=True)
    password = db.StringProperty()
    account_name = db.StringProperty()
    identification_id = db.StringProperty()
    type = db.StringProperty()  # A-Administrator, B-Blog
    status = db.StringProperty()


class IdGen(db.Model):
    name = db.StringProperty(required=True)
    value = db.IntegerProperty(required=True)
