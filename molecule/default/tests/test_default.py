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
