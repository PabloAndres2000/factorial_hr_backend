# Detectar el sistema operativo
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

# Comandos específicos para cada sistema operativo
ifeq ($(DETECTED_OS),Windows)
    RM := del /q
    MKDIR := mkdir
    DOCKER_COMPOSE := docker-compose.exe
else
    RM := rm -f
    MKDIR := mkdir -p
    DOCKER_COMPOSE := docker-compose
endif

# Define los entornos disponibles
ENVS := local qa prod

# Obtiene el entorno desde la línea de comandos o utiliza "local" como predeterminado
ENV ?= local

.PHONY: help up build down bash set-env k8s-apply k8s-verify k8s-describe-pod k8s-delete

help:
	@echo "Uso make para contenedores docker: make (up, down, bash o build) ENV=local, qa o prod"
	@echo "Objetivos disponibles:"
	@echo "  up            : Iniciar contenedores en el entorno $(ENV)"
	@echo "  build         : Construir imágenes de Docker para el entorno $(ENV)"
	@echo "  down          : Detener y eliminar contenedores en el entorno $(ENV)"
	@echo "  bash          : Acceder al shell de contenedores en el entorno $(ENV)"
	@echo "  k8s-apply     : Aplicando configuración de Kubernetes para el entorno $(ENV)"
	@echo "  k8s-verify    : Verificando el estado de los recursos en Kubernetes para el entorno $(ENV)"
	@echo "  k8s-describe-pod : Verifica el comportamiento de un pod(solo ingresa el nombre del pod, ejemplo: nginx-deployment-f75547dfb-8cw26)"
	@echo "  k8s-delete    : Eliminando recursos de Kubernetes para el entorno $(ENV)"

up:
	$(DOCKER_COMPOSE) -f compose/$(ENV).yml up -d

build: down
	$(DOCKER_COMPOSE) -f compose/$(ENV).yml build

down:
	$(DOCKER_COMPOSE) -f compose/$(ENV).yml down --remove-orphans

bash:
	$(DOCKER_COMPOSE) -f compose/$(ENV).yml exec -it electronic_book_$(ENV) /bin/bash

.PHONY: k8s-verify
k8s-verify:
	@echo "Verificando el estado de los recursos en Kubernetes para el entorno $(ENV)"
	kubectl get pods
	kubectl get services
	kubectl get deployments

.PHONY: k8s-describe-pod
k8s-describe-pod:
	@read -p "Ingresa el nombre del pod que deseas revisar: " pod_name; \
	(kubectl describe pod $$pod_name) || (kubectl describe pod -f .kube/services-${ENV}/$$pod_name) || (kubectl describe pod -f .kube/$$pod_name)



.PHONY: k8s-apply
k8s-apply:
	@echo "Aplicando configuración de Kubernetes para el entorno $(ENV)"
	kubectl apply -f .kube/service-${ENV}.yaml
	kubectl apply -f .kube/${ENV}-deployment.yaml

.PHONY: k8s-delete
k8s-delete:
	@echo "Eliminando recursos de Kubernetes para el entorno $(ENV)"
	kubectl delete -f .kube/service-${ENV}.yaml
	kubectl delete -f .kube/${ENV}-deployment.yaml

