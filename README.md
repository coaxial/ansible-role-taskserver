Taskserver role
=========

Deploy a [taskwarrior](https://taskwarrior.org) taskserver with optional hourly
backups to a borg repository.

Requirements
------------

An Ubuntu host with Docker and docker-compose installed.

Role Variables
--------------

name | default value | possible values | purpose
---|---|---|---
td__borg_passcommand | `cat /borgmatic/passphrase` | any valid sh command | run borg without prompting for a passphrase
td__borg_passphrase | none, must be defined | any string | populate the `/borgmatic/passphrase` file for unattended borg operation
td__borg_url | none, must be defined | any valid borg url, i.e. `user@borg.example.com:myrepo` | defines the borg repo to use
td__borgmatic_project_src | `/opt/docker-borgmatic` | any valid path | defines where the borgmatic repo will be cloned
td__cert_bits | `4096` | any valid GnuTLS bit number | used to generate the certificates
td__cert_country | none, must be set | any string | country field in the generated certificates
td__cert_expiration_days | `365` | any number of days | defines how long the certificate will be valid for
td__cert_locality | none, must be set | any string | defines the locality field in the generated certificates
td__cert_organization | none, must be set | any string | defines the organization field in the generated certificates
td__cert_state | none, must be set | any string | defines the state field in the generated certificates
td__enable_backups | `true` | boolean | whether to enable hourly borg backups
td__fetch_client_files | `true` | boolean | whether to fetch the new taskserver user certificates and uuid necessary for configuring the taskwarrior client
td__fqdn | none, must be set | any valid FQDN (must resolve with DNS) | sets the container's hostname and is used as the certificates' CN. Must match the FQDN the client uses to connect to the server
td__orgname | none, must be set | any string | defines the taskserver organization
td__project_src | `/opt/docker-taskd-service` | any valid path | defines where the `docker-taskd-service` repo will be cloned
td__service_name | value of `td__fqdn` | any string | used to name borg backups
td__taskdata_volname | `docker-taskd-service_taskddata` | the docker-compose name for the `taskddata` volume created by `docker-taskd-service` | tells the backup service where to find taskd's data. No need to change unless `td__project_src` has been changed
td__username | `user` | any string | username to create in the taskserver

Role files
----------

name | purpose
---|---
`ssh/id_rsa{,pub}` | ssh keys to connect to the borg repo (only if `td__enable_backups`)
`ssh/known_hosts` | ssh fingerprint for borg repo host (only if `td__enable_backups`)

Dependencies
------------

n/a

Example Playbook
----------------

    - hosts: servers
      become: true
      vars:
        td__fqdn: taskw.example.org
        td__orgname: example org
        td__username: myself
        td__cert_organization: example org
        td__cert_country: CA
        td__cert_state: ON
        td__cert_locality: Toronto
        td__borg_url: user@borg.example.org:tasksrv
        td__borg_passphrase: sup3rs3cure
      roles:
         - coaxial.taskserver

Once the playbook has run, the client configuration files will be in `client_files/`, unless `td__fetch_client_files` was set to false.

Refer to the [taskwarrior documentation](https://gitpitch.com/GothenburgBitFactory/taskserver-setup#/14) to configure the client.

License
-------

BSD

Author Information
------------------

Coaxial<[64b.it](https://64b.it)>
