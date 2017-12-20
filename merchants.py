import requests
import json

DATAURL = 'https://backend-challenge-summer-2018.herokuapp.com/challenges.json'


def getData(url, param):
    # Read JSON from URL
    r = requests.get(url, params=param)
    return r.json()


class MenuList(object):

    def __init__(self, data):
        self.root_id = data
        self.children = []

    def add_child(self, obj):
        if type(obj) is list:
            self.children = self.children + obj
        elif obj not in self.children:
            self.children.append(obj)

    def is_valid(self):
        return self.root_id in self.children

    def is_in_children(self, id):
        return id in self.children

    def is_mergeable(self, menulist):
        return self.is_in_children(menulist.root_id) or self.root_id == menulist.root_id or menulist.is_in_children(self.root_id)

    def merge_menulist(self, menulist):
        if self.is_mergeable(menulist):
            self.add_child(menulist.children)
            if menulist.is_in_children(self.root_id):
                self.root_id = menulist.root_id
        return self

    def get_format(self):
        data = {}
        data['root_id'] = self.root_id
        data['children'] = self.children
        return json.dumps(data)


def validateMenu(menus):
    menuList = []
    for menu in menus:
        id = menu.get('id')
        parentID = menu.get('parent_id', 0)
        childrenIDs = menu.get('child_ids', [])
        root_id = id if parentID == 0 else parentID
        m = MenuList(root_id)
        m.add_child(childrenIDs)
        mergeable_list = [
            menuitem for menuitem in menuList if menuitem.is_mergeable(m)]
        if len(mergeable_list) == 0:
            menuList.append(m)
        else:
            for menuitem in mergeable_list:
                menuitem = menuitem.merge_menulist(m)

    return menuList


def findNextURLParam(pagination):
    if pagination['current_page'] * pagination['per_page'] <= pagination['total']:
        return {'page': pagination['current_page'] + 1}
    else:
        return False


def findInvalidateMenus(url, param={}, invalidateMenu=[]):
    data = getData(url, param)
    nextURLParam = findNextURLParam(data['pagination'])
    invalidateMenu += validateMenu(data['menus'])
    if nextURLParam:
        return findInvalidateMenus(url, nextURLParam, invalidateMenu)

    return invalidateMenu


def main():
    invalidatedMenu = []
    data = findInvalidateMenus(DATAURL, {}, invalidatedMenu)
    for item in data:
        print item.get_format()

main()
