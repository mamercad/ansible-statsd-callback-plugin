.PHONY: statsd
statsd:
	docker run --rm -it \
		--name graphite \
		-p 8000:80 \
		-p 2003-2004:2003-2004 \
		-p 2023-2024:2023-2024 \
		-p 8125:8125/udp \
		-p 8126:8126 \
		graphiteapp/graphite-statsd

.PHONY: statsd-exporter
statsd-exporter:
	docker run --rm -it -p 9102:9102 -p 9125:9125 -p 9125:9125/udp \
					-v /Users/mmercado/src/github.internal.digitalocean.com/mmercado/ansible-statsd-callback-plugin/statsd_mapping.yml:/tmp/statsd_mapping.yml \
					prom/statsd-exporter --statsd.mapping-config=/tmp/statsd_mapping.yml

.PHONY: test
test:
	ANSIBLE_PYTHON_INTERPRETER=/Users/mmercado/.pyenv/shims/python3 ansible-playbook -i localhost, -c local ping.yml -v
