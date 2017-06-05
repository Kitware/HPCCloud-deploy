## Enabling MongoDB authentication and Role-Based Access Control

The following variables can be used to enable MongoDB authentication and Role-Based Access Control. This is the first step in securing a MongoDB deployment.
These variables can be added to ```ansible/group_vars/all``` it is recommended to use [Vault](http://docs.ansible.com/ansible/playbooks_vault.html) this encrypt these passwords.

| parameter                  | required | comments                                                                                                                                                                                                                                                                                                                                           |
| -------------------------- | -------- | -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mongo_admin_user           | no       | The username that will be used for the MongoDB administrator account. The presence of this variable will switch on authentication. This user is given the [userAdminAnyDatabase](https://docs.mongodb.com/manual/reference/built-in-roles/#userAdminAnyDatabase) role.
| mongo_admin_password       | no       | The MongoDB administrator password.
| mongo_girder_user          | no       | The username for the user that Girder will use to connect to MongoDB. This user has the [readWrite](https://docs.mongodb.com/manual/reference/built-in-roles/#readWrite) on the girder database.                                                  |
| mongo_girder_password      | no       | The Girder user password.

