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
        assert host.file("/opt/docker-taskd-service" + f).exists


def test_borgmatic_settings(host):
    files = [
        'borgmatic/before-backup',
        'borgmatic/after-backup',
        'borgmatic/failed-backup',
        'borgmatic/config.yaml',
        'borgmatic/passphrase',
        'docker-compose.data-vol.yml',
    ]

    for f in files:
        assert host.file("/opt/docker-borgmatic" + f).exists
