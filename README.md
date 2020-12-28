# Ansible StatsD callback plugin

This Ansible callback plugin sends Ansible task metrics to StatsD.

For development/testing, one could experiment in Docker like so:

```bash
$ docker run --rm -it \
-p 9102:9102 -p 9125:9125 -p 9125:9125/udp \
-v $(shell pwd)/statsd_mapping.yml:/tmp/statsd_mapping.yml \
prom/statsd-exporter --statsd.mapping-config=/tmp/statsd_mapping.yml
```

An example StatsD mapping manifest (for the Prometheus Exporter):

```yaml
mappings:
  - match: "ansible.playbook_start.*.*.*.*.*.*"
      name: "ansible_playbook_start"
      labels:
      project: "$1"
      playbook: "$2"
      revision: "$3"
      basedir: "$4"
      filename: "$5"
      entries: "$6"
  - match: "ansible.runner_ok.*.*.*.*.*.*"
      name: "ansible_runner_ok"
      labels:
      project: "$1"
      playbook: "$2"
      revision: "$3"
      host: "$4"
      task: "$5"
      changed: "$6"
  - match: "ansible.runner_failed.*.*.*.*.*.*"
      name: "ansible_runner_failed"
      labels:
      project: "$1"
      playbook: "$2"
      revision: "$3"
      host: "$4"
      task: "$5"
      changed: "$6"
  - match: "ansible.playbook_stats.*.*.*.*.*"
      name: "ansible_playbook_stats"
      labels:
      project: "$1"
      playbook: "$2"
      revision: "$3"
      state: "$4"
      host: "$5"
```

This plugin will have to be whitelisted in ansible.cfg.

```ini
[defaults]
callback_whitelist = statsd
```

For example, after running Ansible like this:

```bash
$ STATSD_HOST=127.0.0.1 \
STATSD_PORT=9125 \
STATSD_PROJECT="ansible-statsd-callback-plugin" \
STATSD_PLAYBOOK="ping.yml" \
STATSD_REVISION="dev" \
ansible-playbook -i inventory.yml ping.yml
```

We'll end up with Prometheus metrics which look like this:

```bash
$ http localhost:9102/metrics | grep ^ansible
ansible_playbook_start{basedir="_Users_mmercado_src_github_internal_digitalocean_com_mmercado_ansible-statsd-callback-plugin",entries="all",filename="ping_yml",playbook="ping_yml",project="ansible_statsd_callback_plugin",revision="dev"} 1
ansible_playbook_stats{host="localhost",playbook="ping_yml",project="ansible_statsd_callback_plugin",revision="dev",state="failures"} 1
ansible_playbook_stats{host="localhost",playbook="ping_yml",project="ansible_statsd_callback_plugin",revision="dev",state="ok"} 1
ansible_playbook_stats{host="localhost",playbook="ping_yml",project="ansible_statsd_callback_plugin",revision="dev",state="processed"} 1
ansible_runner_failed{changed="False",host="localhost",playbook="ping_yml",project="ansible_statsd_callback_plugin",revision="dev",task="fail"} 1
ansible_runner_ok{changed="False",host="localhost",playbook="ping_yml",project="ansible_statsd_callback_plugin",revision="dev",task="Hello World"} 1
ansible_runner_ok{changed="False",host="localhost",playbook="ping_yml",project="ansible_statsd_callback_plugin",revision="dev",task="ping"} 1
```
