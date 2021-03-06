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
import random
import string

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

    def create_collection(self, name, description=None):
        url = '%s/collection' % self._base_url
        params = {'name': name}

        if description:
            params['description'] = description

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

    def get_folder_id(self, name, parent_id, parent_type='collection'):
        url = '%s/folder' % self._base_url
        params = {
            'name': name,
            'parentId': parent_id,
            'parentType': parent_type
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

    def grant_folder_user_access(self, folder_id, user_ids, level=2):
        users = []

        for i in user_ids:
            users.append({ 'id': i, 'level': level })

        access = {'users': users}

        url = '%s/folder/%s/access' % (self._base_url, folder_id)
        r = requests.put(url, params={'access': json.dumps(access)}, headers=self._headers)
        self._check_response(r)

    def grant_folder_group_access(self, folder_id, group_ids, level=2):
        groups = []

        for i in group_ids:
            groups.append({ 'id': i, 'level': level })

        access = {'groups': groups}

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

    def update_script_access(self, script_id, user_permissions, group_permissions):
        permissions = {
            'users': user_permissions,
            'groups': group_permissions
        }

        url = '%s/scripts/%s/access' % (self._base_url, script_id)

        r = requests.put(url, json=permissions, headers=self._headers)
        self._check_response(r)

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
    hpccloud_password = config.hpccloud_password
    config_dir = config.config_dir
    script_dir = config.scripts_dir

    client = GirderClient(url)

    try:
        client.create_user('hpccloud', hpccloud_password, 'hpccloud@kitware.com', 'hpccloud',
                        'hpccloud')
    except requests.exceptions.HTTPError:
        pass

    client.authenticate('hpccloud', hpccloud_password)

    # Create cumulus user
    cumulus_password = ''.join(random.SystemRandom()
                            .choice(string.ascii_uppercase +
                                    string.digits) for _ in range(64))
    try:
        client.create_user('cumulus', cumulus_password, 'cumulus@kitware.com', 'cumulus',
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

    if not config.open_reg:
        # Close of instance
        client.set_system_property('core.registration_policy', 'closed')

    plugins = ['cumulus', 'pvwproxy', 'task', 'register', 'sftp', 'newt']

    hpccloud_client_plugin_path = os.path.join(config.hpccloud_repo, 'server')
    if os.path.exists(hpccloud_client_plugin_path):
        plugins.append('hpccloud')

    client.enable_plugins(plugins)

    # Now restart the server to enable the plugins
    client.restart_girder()

    if 'hpccloud' in plugins:
        return

    client.set_system_property('pvwproxy.proxy_file_path', '/opt/hpccloud/proxy')

    # Now restart the server to enable this setting
    client.restart_girder()

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

    try:
        client.create_group('hydra-th-members')
    except requests.exceptions.HTTPError:
        pass

    hydra = client.get_group_id('hydra-th-members')

    client.add_user_to_group(user_001, hydra)
    client.add_user_to_group(user_002, hydra)

    # Here is an example hierarchy that can be used:
    #
    #   (Collections)
    #     - hydra-th (can-edit: hydra-th-members)
    #         + (Folders)
    #             - user001 (can-edit: user001)
    #             - user002 (can-edit: user002)
    #             - Core simulation team (can-edit: user001, user002)
    #             - Multi-scale simulation team (can-edit: user001)

    try:
        client.create_collection('hydra-th', description='Nuclear Energy simulation')
    except requests.exceptions.HTTPError:
        pass

    hydra_collection = client.get_collection_id('hydra-th')

    try:
        client.create_folder('tasks', hydra_collection)
    except requests.exceptions.HTTPError:
        pass

    try:
        client.create_folder('Core simulation team', hydra_collection)
    except requests.exceptions.HTTPError:
        pass

    tasks_folder = client.get_folder_id('tasks', hydra_collection)
    core_folder = client.get_folder_id('Core simulation team', hydra_collection)

    client.grant_folder_group_access(core_folder, [hydra])
    client.grant_folder_group_access(tasks_folder, [hydra], level=0)

    # Set up collection perms
    owner = 2
    client.grant_access(hydra_collection, hydra, 'hydra-th-members', owner)

    # Create the assert store
    try:
        client.create_assetstore('data', config.assetstore_dir)
    except requests.exceptions.HTTPError:
        pass

    cumulus_folder = client.get_folder_id('Private', cumulus, 'user')

    meta_config = {}

    # Create scripts
    user_permissions = [{
        'id': cumulus,
        'level': 2
    }]
    group_permissions = [{
            'id': hydra,
            'level': 0
        }
    ]
    for f in os.listdir(script_dir):
        id =  client.create_script(f, os.path.join(script_dir, f))
        client.update_script_access(id, user_permissions, group_permissions)
        f = f.replace('.', '-')
        meta_config[f] = id

    # Create config
    for f in os.listdir(config_dir):
        id = client.create_starcluster_config(f, os.path.join(config_dir, f))
        f = f.replace('.', '-')
        meta_config[f] =  id

    # Create proxy json file
    item = client.get_item('defaultProxies')
    if len(item) == 0:
        item_id = client.create_item(core_folder, 'defaultProxies')
    else:
        item_id = item[0]['_id']

    files = client.get_files(item_id)

    proxy_json = os.path.join(config.cumulus_repo, 'config/defaultProxies.json')
    with open(proxy_json, 'r') as fp:
        if len(files) == 0:
            client.create_file(item_id, fp, 'defaultProxies.json')
        else:
            client.update_file(files[0]['_id'], fp)

    meta_config['defaultProxies'] = item_id

    # Create mesh tagger file
    item = client.get_item('meshTagger')
    if len(item) == 0:
        item_id = client.create_item(core_folder, 'meshTagger')
    else:
        item_id = item[0]['_id']

    files = client.get_files(item_id)

    proxy_json = os.path.join(config.hpccloud_repo, 'scripts/hydra-th/pv_mesh_viewer.py')
    with open(proxy_json, 'r') as fp:
        if len(files) == 0:
            client.create_file(item_id, fp, 'pv_mesh_viewer.py')
        else:
            client.update_file(files[0]['_id'], fp)

    meta_config['meshTagger'] = item_id

    # Upload config data
    client.set_folder_metadata(cumulus_folder, meta_config)

    # Upload the task specs
    spec_item = client.get_item("Specifications")

    if len(spec_item) == 0:
        spec_item_id = client.create_item(tasks_folder, "Specifications")
    else:
        spec_item_id = spec_item[0]['_id']

    task_files = client.get_files(spec_item_id)

    tasks_dir = config.tasks_dir
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

        spec = template(spec, 'defaults.config.id', meta_config['starcluster-default-conf'])
        spec = template(spec, 'defaults.pvw.script.id', meta_config['pvw-sh'])

        hydra_script_id = meta_config['hydra-sh']
        if config.dummy_hydra:
            hydra_script_id = meta_config['dummy-sh']

        spec = template(spec, 'defaults.hydra.script.id', hydra_script_id)
        spec = template(spec, 'defaults.pvserver.script.id', meta_config['pvserver-sh'])
        spec = template(spec, 'defaults.pvw.proxyItem', meta_config['defaultProxies'])
        spec = template(spec, 'defaults.meshtagger.script.id', meta_config['meshtagger-sh'])
        spec = template(spec, 'defaults.meshtagger', meta_config['meshTagger'])

        fp = StringIO(spec)

        try:
            existing_file  = next(x for x in task_files if x['name'] == name)
            client.update_file(existing_file['_id'], fp)
        except StopIteration:
            client.create_file(spec_item_id, fp, name)

if __name__ ==  '__main__':
    parser = argparse.ArgumentParser(description='Command to setup Girder fixtures')

    prefix = '/opt/hpccloud'
    parser.add_argument('--url', help='Base URL for Girder ops', required=True)
    parser.add_argument('--hpccloud_password', help='The password to use for hpccloud', required=True)
    parser.add_argument('--config_dir', help='The directory containing configs to upload', required=True)
    parser.add_argument('--scripts_dir', help='Directory containing scripts to deploy', default=os.path.join(prefix, 'cumulus/scripts/codes'))
    parser.add_argument('--tasks_dir', help='Directory containing tasks to deploy', default=os.path.join(prefix, 'cumulus/tasks'))
    parser.add_argument('--assetstore_dir', help='Directory to use for asset store', default=os.path.join(prefix, 'assetstore'))
    parser.add_argument('--hpccloud_repo', help='Path the HPCCloud repo', default=os.path.join(prefix, 'hpccloud'))
    parser.add_argument('--cumulus_repo', help='Path the HPCCloud repo', default=os.path.join(prefix, 'cumulus'))
    parser.add_argument('--dummy_hydra', help='Use dummy hydra script', action='store_true')
    parser.add_argument('--open_reg', help='Can users register for an account', action='store_true')

    config = parser.parse_args()

    setup(config)

