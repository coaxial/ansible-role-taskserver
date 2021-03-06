import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


taskd_dir = '/opt/docker-taskd-service/'
borgmatic_dir = '/opt/docker-borgmatic-taskserver/'


def test_taskd_presence(host):
    repo = host.file(taskd_dir)

    assert repo.exists


def test_borgmatic_presence(host):
    repo = host.file(borgmatic_dir)

    assert repo.exists


def test_taskd_settings(host):
    files = [
        'taskserver/taskserver.env',
        'docker-compose.hostname-override.yml',
    ]

    for f in files:
        assert host.file(taskd_dir + f).exists


def test_borgmatic_settings(host):
    files = [
        {
            'name': 'borgmatic/before-backup',
            'mode': 0o700,
        },
        {
            'name': 'borgmatic/after-backup',
            'mode': 0o700,
        },
        {
            'name': 'borgmatic/failed-backup',
            'mode': 0o700,
        },
        {
            'name': 'borgmatic/config.yaml',
            'mode': 0o400,
        },
        {
            'name': 'borgmatic/passphrase',
            'mode': 0o400,
        },
        {
            'name': 'docker-compose.data-vol.yml',
            'mode': 0o644
        },
    ]

    for f in files:
        assert host.file(borgmatic_dir + f['name']).exists
        assert host.file(borgmatic_dir + f['name']).mode == f['mode']


def test_ssh_files(host):
    files = [
        'id_rsa',
        'id_rsa.pub',
        'known_hosts',
    ]

    for f in files:
        assert host.file(borgmatic_dir + '/ssh/' + f).exists
        assert host.file(borgmatic_dir + '/ssh/' + f).mode == 0o600


def test_restoration(host):
    # first extract container name and ip, then start a new container and
    # install taskwarrior on it, configure it, and attempt to sync with
    # taskserver from role.

    # cf http://jinja.pocoo.org/docs/2.10/templates/#escaping
    taskserver_container_name_cmd = (
        "docker ps -f 'name=service_taskserver' "
        "{% raw -%}--format='{{.Names}}'{% endraw -%}"
    )
    taskserver_container_name = host.check_output(
        taskserver_container_name_cmd
    )
    # cf http://jinja.pocoo.org/docs/2.10/templates/#escaping
    inspect_format_string = (
        "{% raw -%}{{range .NetworkSettings.Networks}}"
        "{{.IPAddress}}{{end}}{% endraw -%}"
    )
    taskserver_ip_cmd = (
        "docker inspect -f '%s' %s"
        % (inspect_format_string, taskserver_container_name)
    )
    taskserver_ip = host.check_output(taskserver_ip_cmd)
    task_list_cmd = (
        "docker run --rm --network container:%s "
        "-v /opt/docker-taskd-service/taskserver/client_certs/:"
        "/client_files:ro alpine sh "
        "-c '"
        "echo \"%s taskserver\" >> /etc/hosts && "
        "apk --no-cache add task && "
        "yes | task version && "
        "yes | task config taskd.ca /client_files/ca.cert.pem && "
        "yes | task config taskd.certificate /client_files/user.cert.pem && "
        "yes | task config taskd.key /client_files/user.key.pem && "
        "yes | task config taskd.server taskserver:53589 && "
        "yes | task config taskd.credentials -- "
        "My Org/user/$(cat /client_files/user-uuid) && "
        "yes | task sync init"
        "'"
        % (
            taskserver_container_name, taskserver_ip
        )
    )

    task_sync = host.run(task_list_cmd)

    assert "Sync successful." in task_sync.stderr
