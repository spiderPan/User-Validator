import requests

DATAURL = 'https://backend-challenge-winter-2017.herokuapp.com/customers.json'


def getData(url, param):
    # Read JSON from URL
    r = requests.get(url, params=param)
    return r.json()


def validateUser(rules, users):
    # find out invalidated user
    invalidateUser = []
    for user in users:
        invalid_fields = []
        userID = user.get('id', 0)
        for rule in rules:
            for key, ruleDict in rule.iteritems():
                required = ruleDict.get('required', False)
                dataType = ruleDict.get('type', '')
                length = ruleDict.get('length', {})
                lenMin = length.get('min', False)
                lenMax = length.get('max', False)
                userVal = user.get(key, '')
                if(type(userVal) is unicode):
                    userVal = userVal.encode('utf-8')
                userValStr = str(userVal)

                if (required and len(userValStr) == 0) or ('number' == dataType and type(userVal) is not int) or ('boolean' == dataType and type(userVal) is not bool) or ('string' == dataType and type(userVal) is not str) or (lenMin and len(userValStr) < lenMin) or (lenMax and len(userValStr) > lenMax):
                    invalid_fields.append(key)
        if len(invalid_fields) > 0:
            invalidUserObj = {
                'id': userID,
                'invalid_fields': invalid_fields
            }
            invalidateUser.append(invalidUserObj)
    return invalidateUser


def findNextURLParam(pagination):
    if pagination['current_page'] * pagination['per_page'] <= pagination['total']:
        return {'page': pagination['current_page'] + 1}
    else:
        return False


def findInvalidateUser(url, param={}, invalidateUser=[]):
    data = getData(url, param)
    nextURLParam = findNextURLParam(data['pagination'])
    invalidateUser += validateUser(data['validations'], data['customers'])
    if nextURLParam:
        return findInvalidateUser(url, nextURLParam, invalidateUser)

    return invalidateUser


def main():
    invalidatedUser = []
    data = findInvalidateUser(DATAURL, {}, invalidatedUser)
    print data

main()
