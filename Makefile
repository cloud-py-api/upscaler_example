.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Welcome to Image UpScaler example. Please use \`make <target>\` where <target> is one of"
	@echo " "
	@echo "  Next commands are only for dev environment with nextcloud-docker-dev!"
	@echo "  They should run from the host you are developing on(with activated venv) and not in the container with Nextcloud!"
	@echo "  "
	@echo "  build-push        build image and upload to ghcr.io"
	@echo "  "
	@echo "  deploy28          deploy example to registered 'docker_dev' for Nextcloud 28"
	@echo "  deploy27          deploy example to registered 'docker_dev' for Nextcloud 27"
	@echo "  "
	@echo "  run28             install UpScaler for Nextcloud 28"
	@echo "  run27             install UpScaler for Nextcloud 27"
	@echo "  "
	@echo "  For development of this example use PyCharm run configurations. Development is always set for last Nextcloud."
	@echo "  First run 'upscaler_example' and then 'make register', after that you can use/debug/develop it and easy test."
	@echo "  "
	@echo "  register28        perform registration of running 'upscaler_example' into 'manual_install' deploy daemon."
	@echo "  register27        perform registration of running 'upscaler_example' into 'manual_install' deploy daemon."

.PHONY: build-push
build-push:
	docker login ghcr.io
	docker buildx build --push --platform linux/arm64/v8,linux/amd64 --tag ghcr.io/cloud-py-api/upscaler_example:1.2.0 --tag ghcr.io/cloud-py-api/upscaler_example:latest .

.PHONY: deploy28
deploy28:
	docker exec master-nextcloud-1 sudo -u www-data php occ app_api:app:unregister upscaler_example --silent || true
	docker exec master-nextcloud-1 sudo -u www-data php occ app_api:app:deploy upscaler_example docker_dev \
		--info-xml https://raw.githubusercontent.com/cloud-py-api/upscaler_example/main/appinfo/info.xml

.PHONY: run28
run28:
	docker exec master-nextcloud-1 sudo -u www-data php occ app_api:app:unregister upscaler_example --silent || true
	docker exec master-nextcloud-1 sudo -u www-data php occ app_api:app:register upscaler_example docker_dev \
		--force-scopes \
		--info-xml https://raw.githubusercontent.com/cloud-py-api/upscaler_example/main/appinfo/info.xml

.PHONY: deploy27
deploy27:
	docker exec master-stable27-1 sudo -u www-data php occ app_api:app:unregister upscaler_example --silent || true
	docker exec master-stable27-1 sudo -u www-data php occ app_api:app:deploy upscaler_example docker_dev \
		--info-xml https://raw.githubusercontent.com/cloud-py-api/upscaler_example/main/appinfo/info.xml

.PHONY: run27
run27:
	docker exec master-stable27-1 sudo -u www-data php occ app_api:app:unregister upscaler_example --silent || true
	docker exec master-stable27-1 sudo -u www-data php occ app_api:app:register upscaler_example docker_dev \
		--force-scopes \
		--info-xml https://raw.githubusercontent.com/cloud-py-api/upscaler_example/main/appinfo/info.xml

.PHONY: register28
register28:
	docker exec master-nextcloud-1 sudo -u www-data php occ app_api:app:unregister upscaler_example --silent || true
	docker exec master-nextcloud-1 sudo -u www-data php occ app_api:app:register upscaler_example manual_install --json-info \
  "{\"appid\":\"upscaler_example\",\"name\":\"upscaler_example\",\"daemon_config_name\":\"manual_install\",\"version\":\"1.0.0\",\"secret\":\"12345\",\"host\":\"host.docker.internal\",\"port\":10050,\"scopes\":{\"required\":[\"FILES\", \"NOTIFICATIONS\"],\"optional\":[]},\"protocol\":\"http\",\"system_app\":0}" \
  --force-scopes

.PHONY: register27
register27:
	docker exec master-stable27-1 sudo -u www-data php occ app_api:app:unregister upscaler_example --silent || true
	docker exec master-stable27-1 sudo -u www-data php occ app_api:app:register upscaler_example manual_install --json-info \
  "{\"appid\":\"upscaler_example\",\"name\":\"upscaler_example\",\"daemon_config_name\":\"manual_install\",\"version\":\"1.0.0\",\"secret\":\"12345\",\"host\":\"host.docker.internal\",\"port\":10050,\"scopes\":{\"required\":[\"FILES\", \"NOTIFICATIONS\"],\"optional\":[]},\"protocol\":\"http\",\"system_app\":0}" \
  --force-scopes
