## Enabling MongoDB authentication and Role-Based Access Control

The following variables can be used to enable MongoDB authentication and Role-Based Access Control. This is the first step in securing a MongoDB deployment.
These variables can be added to ```ansible/group_vars/all``` it is recommended to use [Vault](http://docs.ansible.com/ansible/playbooks_vault.html) to encrypt these passwords.

| parameter                  | required | comments                                                                                                                                                                                                                                                                                                                                           |
| -------------------------- | -------- | -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mongodb_admin_user           | no       | The username that will be used for the MongoDB administrator account. The presence of this variable will switch on authentication. This user is given the [userAdminAnyDatabase](https://docs.mongodb.com/manual/reference/built-in-roles/#userAdminAnyDatabase) role.
| mongodb_admin_password       | no       | The MongoDB administrator password.
| mongodb_girder_user          | no       | The username for the user that Girder will use to connect to MongoDB. This user has the [readWrite](https://docs.mongodb.com/manual/reference/built-in-roles/#readWrite) on the girder database.                                                  |
| mongodb_girder_password      | no       | The Girder user password.

## Enabling MongoDB SSL/TLS for encrypt communication

The following variables can be used to enable TLS/SSL encryption for connections between Girder and MongoDB.

| parameter                  | required | comments                                                                                                                                                                                                                                                                                                                                           |
| -------------------------- | -------- | -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
mongodb_ssl_pem_path    | no | The path to the PEM file containing a public key certificate and its associated private key.
mongodb_ssl_self_signed | no | Used to indicate if this is a self-signed certificate. This disables certificate validation. The communications channel will be encrypted but no validation of the servers identity will be performed.
mongodb_ssl_ca_file     | no | The path to the file that contains the root certificate chain from the Certificate Authority.

## Enabling RabbitMQ authentication and Access Control

A default installation of RabbitMQ uses a default user and password and give access to everything. The following variable can be used to remove this default account, create and admin acccount and account for Celery to connect to RabbitMQ with. The Celery user is give access only to the [vhost](https://www.rabbitmq.com/vhosts.html) /celery

| parameter                  | required | comments                                                                                                                                                                                                                                                                                                                                           |
| -------------------------- | -------- | -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| rabbitmq_admin_user           | no       | The username that will be used for the RabbitMQ administrator account. This use had full control of the / vhost, however it can only connect via localhost.
| rabbitmq_admin_user       | no       | The RabbitMQ administrator password.
| rabbitmq_celery_user          | no       | The username for the user that Celery will use to connect to RabbitMQ. This user has read/write access to the /celery vhost.                                                  |
| rabbitmq_celery_password      | no       | The Celery user password.
