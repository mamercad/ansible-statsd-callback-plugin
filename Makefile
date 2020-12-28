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
		-v $(shell pwd)/statsd_mapping.yml:/tmp/statsd_mapping.yml \
		prom/statsd-exporter --statsd.mapping-config=/tmp/statsd_mapping.yml

.PHONY: ansible
ansible:
	STATSD_HOST=127.0.0.1 \
	STATSD_PORT=9125 \
	STATSD_PROJECT="ansible_statsd_callback_plugin" \
	STATSD_PLAYBOOK="ping_yml" \
	STATSD_REVISION="dev" \
	ansible-playbook -i inventory.yml ping.yml

.PHONY: query
query:
	http localhost:9102/metrics | grep ^ansible
