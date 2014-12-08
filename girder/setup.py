import requests
import sys
import json
import argparse
import os
import tempfile
import time
import re
from StringIO import StringIO
from cumulus.task.spec import validate

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

    def enable_plugins(self, names):
        url = '%s/system/plugins' % self._base_url
        r = requests.put(url, params={'plugins': json.dumps(names)}, headers=self._headers)
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


    def grant_access(self, collection_id, group_id, group, level):
        access = {
            'groups': [
                {   'id': group_id,
                    'name': group,
                    'level': level
                }
            ]
        }

        url = '%s/collection/%s/access' % (self._base_url, collection_id)
        r = requests.put(url, params={'access': json.dumps(access)}, headers=self._headers)
        self._check_response(r)

    def grant_folder_user_edit_access(self, folder_id, user_ids):
        users = []

        for i in user_ids:
            users.append({ 'id': i, 'level': 2 })

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

    def update_file(self, file_id, fp):
        data = fp.read()
        url = '%s/file/%s/contents' % (self._base_url, file_id)
        params = {
           'id': file_id,
           'size': len(data)
        }
        r = requests.put(url, params=params, headers=self._headers)
        self._check_response(r)
        upload_id = r.json()['_id']

        params={
            'uploadId': upload_id,
            'offset': 0
        }

        files = {
           "chunk": data
        }

        url = '%s/file/chunk' % self._base_url
        r = requests.post(url, params=params, files=files, headers=self._headers)
        self._check_response(r)


    def create_file(self, itemId, fp, name=None):
        data = fp.read()
        url = '%s/file' % self._base_url

        if not name:
            name = os.path.basename(path)

        params = {
           'parentType': 'item',
           'parentId': itemId ,
           'name': name,
           'size': len(data)
        }
        r = requests.post(url, params=params, headers=self._headers)
        self._check_response(r)
        file_id = r.json()['_id']

        params={
            'uploadId': file_id,
            'offset': 0
        }

        url = '%s/file/chunk' % self._base_url
        files = {
            "chunk": data
        }
        r = requests.post(url, params=params, files=files, headers=self._headers)

        self._check_response(r)

        return file_id

    def get_item(self, text):
        url = '%s/item' % self._base_url
        params = {
           'text': text
        }

        r = requests.get(url, params=params, headers=self._headers)
        self._check_response(r)

        return r.json()

    def get_files(self, item_id):
        url = '%s/item/%s/files' % (self._base_url, item_id)

        r = requests.get(url, headers=self._headers)
        self._check_response(r)

        return r.json()

    def set_folder_metadata(self, item_id, meta):
        url = '%s/folder/%s/metadata' % (self._base_url, item_id)

        r = requests.put(url, json=meta, headers=self._headers)
        self._check_response(r)

    def restart_girder(self):
        url = '%s/system/restart' % self._base_url
        r = requests.put(url, headers=self._headers)
        self._check_response(r)

        up = False
        down = False

        while not up:
            try:
                r = requests.get(url)
                if down:
                    up = True
            except requests.exceptions.ConnectionError:
                down = True
            time.sleep(1)

def setup(config):

    url = config.url
    websimdev_password = config.websimdev_password
    cumulus_password = config.cumulus_password
    config_dir = config.config_dir

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

    client.enable_plugins(['cumulus', 'pvwproxy', 'mesh', 'task'])

    # Now restart the server to enable the plugins
    client.restart_girder()

    client.set_system_property('pvwproxy.proxy_file_path', '/opt/websim/proxy')

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
    except requests.exceptions.HTTPError:
        pass

    try:
        client.create_folder('user002', hydra_collection)
    except requests.exceptions.HTTPError:
        pass

    try:
        client.create_folder('Task', hydra_collection)
    except requests.exceptions.HTTPError:
        pass

    try:
        client.create_folder('Core simulation team', hydra_collection)
    except requests.exceptions.HTTPError:
        pass

    try:
        client.create_folder('Multi-scale simulation team', hydra_collection)
    except requests.exceptions.HTTPError:
        pass


    user001_folder = client.get_folder_id(hydra_collection, 'user001')
    user002_folder = client.get_folder_id(hydra_collection, 'user002')
    task_folder = client.get_folder_id(hydra_collection, 'Task')
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
    owner = 2
    client.grant_access(hydra_collection, hydra, 'hydra-ne-members', owner)
    client.grant_access(hydra_collection, mpas, 'mpas-ocean-members', owner)

    # Create the assert store
    try:
        client.create_assetstore('data', '/opt/websim/assetstore')
    except requests.exceptions.HTTPError:
        pass

    # Create a collection to hold configuration
    try:
        client.create_collection('configuration')
    except requests.exceptions.HTTPError:
        pass

    config_collection = client.get_collection_id('configuration')

    try:
        client.create_folder('cumulus', config_collection)
    except requests.exceptions.HTTPError:
        pass

    cumulus_folder = client.get_folder_id(config_collection, 'cumulus')

    config = {}

    # Create scripts
    script_dir = '/opt/websim/cumulus/scripts'
    for f in os.listdir(script_dir):
        id =  client.create_script(f, os.path.join(script_dir, f))
        f = f.replace('.', '-')
        config[f] = id

    # Create config
    for f in os.listdir(config_dir):
        id = client.create_starcluster_config(f, os.path.join(config_dir, f))
        f = f.replace('.', '-')
        config[f] =  id

    # Create proxy json file
    item = client.get_item('defaultProxies')
    if len(item) == 0:
        item_id = client.create_item(core_folder, 'defaultProxies')
    else:
        item_id = item[0]['_id']

    files = client.get_files(item_id)

    proxy_json = '/opt/websim/cumulus/config/defaultProxies.json'
    with open(proxy_json, 'r') as fp:
        if len(files) == 0:
            client.create_file(item_id, fp)
        else:
            client.update_file(files[0]['_id'], fp)

    config['defaultProxies'] = item_id

    # Upload config data
    client.set_folder_metadata(cumulus_folder, config)

    # Add sample mesh
    try:
        client.create_folder('foobar', user001_folder, 'folder')
    except requests.exceptions.HTTPError:
        pass

    foobar_id = client.get_folder_id(user001_folder, 'foobar')

    mesh_item = client.get_item('mesh')
    if len(mesh_item) == 0:
        mesh_item_id = client.create_item(foobar_id, 'mesh')
    else:
        mesh_item_id = mesh_item[0]['_id']

    files = client.get_files(mesh_item_id)

    fp = StringIO(os.urandom(2048))
    if len(files) == 0:
        client.create_file(mesh_item_id, fp, name='test.mesh')
    else:
        client.update_file(files[0]['_id'], fp)

    # Upload the task specs
    spec_item = client.get_item("Specifications")

    if len(spec_item) == 0:
        spec_item_id = client.create_item(task_folder, "Specifications")
    else:
        spec_item_id = spec_item[0]['_id']

    task_files = client.get_files(spec_item_id)

    tasks_dir = '/opt/websim/cumulus/tasks'
    for f in os.listdir(tasks_dir):
        path = os.path.join(tasks_dir, f)

        name = f.replace('.json', '')

        # Template any defaults
        with open(path, 'r') as fp:
            spec = fp.read()

        # First validate against our schema
        validate(json.loads(spec))

        # For now use regex replace rather than jinja2 because we can't do
        # partial rendering with objects

        def template(spec, key, value):
            return re.sub(r'\{\{\s*%s\s*\}\}' % key, value, spec)

        spec = template(spec, 'defaults.config.id', config['starcluster-default-conf'])
        spec = template(spec, 'defaults.pvw.script.id', config['pvw-sh'])
        spec = template(spec, 'defaults.pvserver.script.id', config['pvserver-sh'])
        spec = template(spec, 'defaults.pvw.proxyItem', config['defaultProxies'])

        fp = StringIO(spec)

        try:
            existing_file  = next(x for x in task_files if x['name'] == name)
            client.update_file(existing_file['_id'], fp)
        except StopIteration:
            client.create_file(spec_item_id, fp, name=name)

if __name__ ==  '__main__':
    parser = argparse.ArgumentParser(description='Command to setup Girder fixtures')

    parser.add_argument('--url', help='Base URL for Girder ops', required=True)
    parser.add_argument('--websimdev_password', help='The password to use for websimdev', required=True)
    parser.add_argument('--cumulus_password', help='The password to use for cumulus', required=True)
    parser.add_argument('--config_dir', help='The directory containing configs to upload', required=True)

    config = parser.parse_args()

    setup(config)

