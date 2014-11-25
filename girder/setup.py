import requests
import sys
import json
import argparse
import os

class GirderClient(object):
    def __init__(self, base_url):
        self._base_url = base_url
        self._headers = None

    def _check_response(self, response):
        if response.status_code != 200:
            if response.headers['Content-Type'] == 'application/json':
                print >> sys.stderr, response.json()
            response.raise_for_status()


    def create_user(self, login, password, email, firstName, lastName, admin=True):
        params = {
            'login': login,
            'email': email,
            'firstName': firstName,
            'lastName': lastName,
            'password': password,
            'admin': admin}

        url = '%s/user' % self._base_url

        headers = {}

        if self._headers:
            headers = self._headers

        r  = requests.post(url, params=params, headers=headers)
        self._check_response(r)

    def create_group(self, name, public=False):
        params = {
            'name': name,
            'public': public}

        url = '%s/group' % self._base_url
        r  = requests.post(url, params=params, headers=self._headers)
        self._check_response(r)

    def add_user_to_group(self, user_id, group_id ):
        params = {
            'id': group_id,
            'userId': user_id,
            'quiet': True,
            'force': True}

        url = '%s/group/%s/invitation' % (self._base_url, group_id)
        r  = requests.post(url, params=params, headers=self._headers)
        self._check_response(r)

    def get_user_id(self, name):
        url = '%s/user' % self._base_url
        r = requests.get(url, params={'text': name}, headers=self._headers)
        self._check_response(r)
        return r.json()[0]['_id']

    def get_group_id(self, name):
        url = '%s/group' % self._base_url
        r = requests.get(url, params={'text': name}, headers=self._headers)
        self._check_response(r)
        return r.json()[0]['_id']

    def enable_plugin(self, name):
        url = '%s/system/plugins' % self._base_url
        names = '["%s"]' % name
        r = requests.put(url, params={'plugins': names}, headers=self._headers)
        self._check_response(r)

    def authenticate(self, user, password):
        url = '%s/user/authentication' % self._base_url
        r = requests.get(url, auth=(user, password))
        self._check_response(r)
        self._token = r.json()['authToken']['token']
        self._headers = {'Girder-Token': self._token}

    def set_system_property(self, name, value):
        url = '%s/system/setting' % self._base_url
        params = {'key': name, 'value': value}
        r = requests.put(url, params, headers=self._headers)
        self._check_response(r)

    def create_collection(self, name):
        url = '%s/collection' % self._base_url
        params = {'name': name}
        r = requests.post(url, params, headers=self._headers)
        self._check_response(r)

    def get_collection_id(self, name):
        url = '%s/collection' % self._base_url
        r = requests.get(url, params={'text': name}, headers=self._headers)
        self._check_response(r)
        return r.json()[0]['_id']

    def create_folder(self, name, parent_id, parent_type='collection'):
        url = '%s/folder' % self._base_url
        params = {
            'name': name,
            'parentId': parent_id,
            'parentType': parent_type
        }
        r = requests.post(url, params, headers=self._headers)
        self._check_response(r)

    def get_folder_id(self, parent_id, name):
        url = '%s/folder' % self._base_url
        params = {
            'text': name,
            'parentId': parent_id
            }
        r = requests.get(url, params=params, headers=self._headers)
        self._check_response(r)
        return r.json()[0]['_id']


    def grant_edit_access(self, collection_id, group_id, group):
        access = {
            'groups': [
                {   'id': group_id,
                    'name': group,
                    'level': 1
                }
            ]
        }

        url = '%s/collection/%s/access' % (self._base_url, collection_id)
        r = requests.put(url, params={'access': json.dumps(access)}, headers=self._headers)
        self._check_response(r)

    def grant_folder_user_edit_access(self, folder_id, user_ids):
        users = []

        for i in user_ids:
            users.append({ 'id': i, 'level': 1})

        access = {'users': users}

        url = '%s/folder/%s/access' % (self._base_url, folder_id)
        r = requests.put(url, params={'access': json.dumps(access)}, headers=self._headers)
        self._check_response(r)

    def create_assetstore(self, name, path):
        url = '%s/assetstore' % self._base_url
        params = {
            'type': 0,
            'name': name,
            'root': path
        }

        r = requests.post(url, params=params, headers=self._headers)
        self._check_response(r)

    def create_script(self, name, path):
        url = '%s/scripts' % self._base_url
        body = {
            'name': name,
        }

        r = requests.post(url, json=body, headers=self._headers)
        self._check_response(r)
        script_id = r.json()['_id']

        # Now import the script
        url = '%s/scripts/%s/import' % (self._base_url, script_id)
        with open(path, 'r') as fp:
            r = requests.patch(url, data=fp.read(), headers=self._headers)
            self._check_response(r)

        return script_id

    def create_starcluster_config(self, name, path):
        url = '%s/starcluster-configs' % self._base_url
        body = {
            'name': name,
            'config': {}
        }

        r = requests.post(url, json=body, headers=self._headers)
        self._check_response(r)
        config_id = r.json()['_id']

        # Now import the config
        url = '%s/starcluster-configs/%s/import' % (self._base_url, config_id)
        with open(path, 'r') as fp:
            r = requests.patch(url, data=fp.read(), headers=self._headers)
            self._check_response(r)

        return config_id

    def create_item(self, folderId, name):
        url = '%s/item' % self._base_url
        params = {
           'folderId': folderId,
           'name': name
        }
        r = requests.post(url, params=params, headers=self._headers)
        self._check_response(r)
        item_id = r.json()['_id']

        return item_id

    def upload_file(self, itemId, path):
        url = '%s/file' % self._base_url
        with open(path, 'r') as fp:
            data = fp.read()

        params = {
           'parentType': 'item',
           'parentId': itemId ,
           'name': os.path.basename(path),
           'size': len(data)
        }
        r = requests.post(url, params=params, headers=self._headers)
        self._check_response(r)
        file_id = r.json()['_id']

        params={
            'uploadId': file_id,
            'offset': 0,
            'chunk': data
        }

        url = '%s/file/chunk' % self._base_url
        r = requests.post(url, params=params, headers=self._headers)
        self._check_response(r)

    def get_item(self, text):
         url = '%s/item' % self._base_url
         params = {
            'text': text
         }

         r = requests.get(url, params=params, headers=self._headers)
         self._check_response(r)

         return r.json()

def setup(url, websimdev_password, cumulus_password):

    client = GirderClient(url)

    try:
        client.create_user('websimdev', websimdev_password, 'websimdev@kitware.com', 'websimdev',
                        'websimdev')
    except requests.exceptions.HTTPError:
        pass

    client.authenticate('websimdev', cumulus_password)

    # Create cumulus user
    try:
        client.create_user('cumulus', websimdev_password, 'cumulus@kitware.com', 'cumulus',
                        'cumulus')
    except requests.exceptions.HTTPError:
        pass

    cumulus = client.get_user_id('cumulus')

    # Create cumulus group
    try:
        client.create_group('cumulus')
    except requests.exceptions.HTTPError:
        pass

    cumulus_group = client.get_group_id('cumulus')

    # Add user to cumulus group
    client.add_user_to_group(cumulus, cumulus_group)

    # Close of instance
    client.set_system_property('core.registration_policy', 'closed')


    client.enable_plugin('cumulus')
    client.enable_plugin('pvwproxy')

    # The first time this will fail! Girder requres a restart after enabling
    # plugins.
    try:
        client.set_system_property('pvwproxy.proxy_file_path', '/opt/websim/proxy')
    except requests.exceptions.HTTPError:
        pass

    # Now setup dev fixtures for client
    # For development purpose 3 users should be created:
    #     - User 001:
    #         Login       : user001
    #         Password    : user001001
    #         E-Mail      : user001@nowhere.com
    #         First Name  : User
    #         Last Name   : 001
    #     - User 002:
    #         Login       : user002
    #         Password    : user002002
    #         E-Mail      : user002@nowhere.com
    #         First Name  : User
    #         Last Name   : 002
    #     - User 003:
    #         Login       : user003
    #         Password    : user003003
    #         E-Mail      : user003@nowhere.com
    #         First Name  : User
    #         Last Name   : 003
    try:
        client.create_user('user001', 'user001001', 'user001@nowhere.com', 'User',
                        '001', admin=False)
    except requests.exceptions.HTTPError:
        pass
    try:
        client.create_user('user002', 'user002002', 'user002@nowhere.com', 'User',
                        '002', admin=False)
    except requests.exceptions.HTTPError:
        pass
    try:
        client.create_user('user003', 'user003003', 'user003@nowhere.com', 'User',
                        '003', admin=False)
    except requests.exceptions.HTTPError:
        pass

    user_001 = client.get_user_id('user001')
    user_002 = client.get_user_id('user002')
    user_003 = client.get_user_id('user003')

    #   (Groups)
    #     - hydra-ne-members: user001, user002
    #     - mpas-ocean-members: user001, user003

    try:
        client.create_group('hydra-ne-members')
    except requests.exceptions.HTTPError:
        pass
    try:
        client.create_group('mpas-ocean-members')
    except requests.exceptions.HTTPError:
        pass

    hydra = client.get_group_id('hydra-ne-members')
    mpas = client.get_group_id('mpas-ocean-members')

    client.add_user_to_group(user_001, hydra)
    client.add_user_to_group(user_002, hydra)
    client.add_user_to_group(user_001, mpas)
    client.add_user_to_group(user_003, mpas)

    # Here is an example hierarchy that can be used:
    #
    #   (Collections)
    #     - hydra-ne (can-edit: hydra-ne-members)
    #         + (Folders)
    #             - user001 (can-edit: user001)
    #             - user002 (can-edit: user002)
    #             - Core simulation team (can-edit: user001, user002)
    #             - Multi-scale simulation team (can-edit: user001)
    #     - mpas-ocean (can-edit: mpas-ocean-members)
    #         + (Folders)
    #             - user001 (can-edit: user001)
    #             - user003 (can-edit: user003)
    #             - Oceanic climate (can-edit: user001, user003)
    #             - El Nino (can-edit: user003)

    try:
        client.create_collection('hydra-ne')
    except requests.exceptions.HTTPError:
        pass

    try:
        client.create_collection('mpas-ocean')
    except requests.exceptions.HTTPError:
        pass

    hydra_collection = client.get_collection_id('hydra-ne')
    mpas_collection = client.get_collection_id('mpas-ocean')

    try:
        client.create_folder('user001', hydra_collection)
        client.create_folder('user002', hydra_collection)
        client.create_folder('Core simulation team', hydra_collection)
        client.create_folder('Multi-scale simulation team', hydra_collection)
    except requests.exceptions.HTTPError:
        pass

    user001_folder = client.get_folder_id(hydra_collection, 'user001')
    user002_folder = client.get_folder_id(hydra_collection, 'user002')
    core_folder = client.get_folder_id(hydra_collection, 'Core simulation team')
    multi_folder = client.get_folder_id(hydra_collection, 'Multi-scale simulation team')

    client.grant_folder_user_edit_access(user001_folder, [user_001])
    client.grant_folder_user_edit_access(user002_folder, [user_002])
    client.grant_folder_user_edit_access(core_folder, [user_001, user_002])
    client.grant_folder_user_edit_access(multi_folder, [user_001])

    try:
        client.create_folder('user001', mpas_collection)
        client.create_folder('user003', mpas_collection)
        client.create_folder('Oceanic climate', mpas_collection)
        client.create_folder('El Nino', mpas_collection)
    except requests.exceptions.HTTPError:
        pass

    user001_folder = client.get_folder_id(mpas_collection, 'user001')
    user003_folder = client.get_folder_id(mpas_collection, 'user003')
    ocenanic_folder = client.get_folder_id(mpas_collection, 'Oceanic climate')
    elino_folder = client.get_folder_id(mpas_collection, 'El Nino')

    client.grant_folder_user_edit_access(user001_folder, [user_001])
    client.grant_folder_user_edit_access(user003_folder, [user_003])
    client.grant_folder_user_edit_access(ocenanic_folder, [user_001, user_003])
    client.grant_folder_user_edit_access(elino_folder, [user_003])

    # Set up collection perms

    client.grant_edit_access(hydra_collection, hydra, 'hydra-ne-members')
    client.grant_edit_access(hydra_collection, mpas, 'mpas-ocean-members')

    # Create the assert store
    try:
        client.create_assetstore('data', '/opt/websim/assetstore')
    except requests.exceptions.HTTPError:
        pass

    # Create scripts
    script_dir = '/opt/websim/cumulus/scripts'
    for f in os.listdir(script_dir):
        print '%s: %s' % (f, client.create_script(f, os.path.join(script_dir, f)))

    # Create config
    config_dir = '/tmp/starcluster-config'
    for f in os.listdir(config_dir):
        name = os.path.basename(f)
        print '%s: %s' % (name, client.create_starcluster_config(f, os.path.join(config_dir, f)))

    # Create proxy json file
    item = client.get_item('defaultProxies')
    if len(item) == 0:
        item_id = client.create_item(core_folder, 'defaultProxies')
    else:
        item_id = item[0]['_id']

    print 'proxy item: %s' % item_id

    client.upload_file(item_id, '/opt/websim/cumulus/config/defaultProxies.json')


if __name__ ==  '__main__':
    parser = argparse.ArgumentParser(description='Command to setup Girder fixtures')

    parser.add_argument('--url', help='Base URL for Girder ops', required=True)
    parser.add_argument('--websimdev_password', help='The password to use for websimdev', required=True)
    parser.add_argument('--cumulus_password', help='The password to use for cumulus', required=True)

    config = parser.parse_args()

    setup(config.url, config.websimdev_password, config.cumulus_password)

