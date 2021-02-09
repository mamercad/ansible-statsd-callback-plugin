# Ansible StatsD callback plugin

This Ansible callback plugin sends Ansible task metrics to StatsD.

For development/testing, one could experiment in Docker like so:

```bash
$ docker run --rm -it \
-p 9102:9102 -p 9125:9125 -p 9125:9125/udp \
-v $(pwd)/statsd_mapping.yml:/tmp/statsd_mapping.yml \
prom/statsd-exporter --statsd.mapping-config=/tmp/statsd_mapping.yml
```

An example StatsD mapping manifest (for the Prometheus Exporter):

```yaml
mappings:
  - match: "ansible.playbook_start.*.*.*"
    name: "ansible_playbook_start"
    labels:
      basedir: "$1"
      playbook: "$2"
      entries: "$3"
  - match: "ansible.runner_ok.*.*.*.*.*"
    name: "ansible_runner_ok"
    labels:
      basedir: "$1"
      playbook: "$2"
      host: "$3"
      task: "$4"
      changed: "$5"
  - match: "ansible.runner_failed.*.*.*.*.*"
    name: "ansible_runner_failed"
    labels:
      basedir: "$1"
      playbook: "$2"
      host: "$3"
      task: "$4"
      changed: "$5"
  - match: "ansible.playbook_stats.*.*.*.*"
    name: "ansible_playbook_stats"
    labels:
      basedir: "$1"
      playbook: "$2"
      state: "$3"
      host: "$4"
```

This plugin will have to be whitelisted in ansible.cfg.

```ini
[defaults]
callback_whitelist = statsd
```

For example, after running Ansible like this:

```bash
❯ STATSD_HOST=127.0.0.1 \
STATSD_PORT=9125 \
ansible-playbook -i inventory.yml ping.yml
```

We'll end up with Prometheus metrics which look like this:

```bash
❯ http localhost:9102/metrics | grep ^ansible
ansible_playbook_start{basedir="ansible-statsd-callback-plugin",entries="all",playbook="ping"} 1
ansible_playbook_stats{basedir="ansible-statsd-callback-plugin",host="localhost",playbook="ping",state="failures"} 1
ansible_playbook_stats{basedir="ansible-statsd-callback-plugin",host="localhost",playbook="ping",state="ok"} 1
ansible_playbook_stats{basedir="ansible-statsd-callback-plugin",host="localhost",playbook="ping",state="processed"} 1
ansible_runner_failed{basedir="ansible-statsd-callback-plugin",changed="False",host="localhost",playbook="ping",task="fail"} 1
ansible_runner_ok{basedir="ansible-statsd-callback-plugin",changed="False",host="localhost",playbook="ping",task="Hello World"} 1
ansible_runner_ok{basedir="ansible-statsd-callback-plugin",changed="False",host="localhost",playbook="ping",task="ping"} 1
```
