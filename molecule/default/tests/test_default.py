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
    host.check_output(
        "cd /opt/docker-taskd-service && "
        "export COMPOSE_INTERACTIVE_NO_CLI=1 && "
        "docker-compose logs && "
        "docker-compose exec taskserver sh -c '"
        "ls -clash /var/taskd && "
        "apk --no-cache add tree && "
        "tree /var/taskd'"
    )
    # base_dir = '/home/travis/build/coaxial/ansible-role-taskserver'
    # host.check_output("sudo apt install tree -yq")
    # assert host.check_output("tree /") == 'foo'
    # assert host.check_output("tree %s" % base_dir) == 'foo'
    # host.check_output("ls -clash %s" % base_dir) == 'foo'
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
        "ls -clash /client_files && "
        "echo \"%s taskd.example.com\" >> /etc/hosts && "
        "ping -c 3 taskd.example.com && apk --no-cache add task && "
        "yes | task version && "
        "yes | task config taskd.ca /client_files/ca.cert.pem && "
        "yes | task config taskd.certificate /client_files/user.cert.pem && "
        "yes | task config taskd.key /client_files/user.key.pem && "
        "yes | task config taskd.server taskd.example.org:53589 && "
        "yes | task config taskd.credentials -- "
        "My Org/user/$(cat /client_files/user-uuid) && "
        "task diag && "
        "yes | task sync init'" % (
            taskserver_container_name, taskserver_ip
        )
    )

    tasks = host.check_output(task_list_cmd)

    assert tasks == 'foo'
