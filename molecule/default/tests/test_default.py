import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_taskd_presence(host):
    repo = host.file('/opt/docker-taskd-service')

    assert repo.exists


def test_borgmatic_presence(host):
    repo = host.file('/opt/docker-borgmatic')

    assert repo.exists


def test_taskd_settings(host):
    files = [
        'taskserver/taskserver.env',
        'docker-compose.hostname-override.yml',
    ]

    for f in files:
        assert host.file("/opt/docker-taskd-service/" + f).exists


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
        assert host.file("/opt/docker-borgmatic/" + f['name']).exists
        assert host.file(
            "/opt/docker-borgmatic/" + f['name']
        ).mode == f['mode']


def test_ssh_files(host):
    files = [
        'id_rsa',
        'id_rsa.pub',
        'known_hosts',
    ]

    for f in files:
        assert host.file("/opt/docker-borgmatic/ssh/" + f).exists
        assert host.file("/opt/docker-borgmatic/ssh/" + f).mode == 0o600
