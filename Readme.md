# Local Kubernetes DevOps Lab

![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Ansible](https://img.shields.io/badge/ansible-%231A1918.svg?style=for-the-badge&logo=ansible&logoColor=white)
![GitLab CI](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)
![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)

Полнофункциональный локальный Kubernetes кластер, развернутый с использованием подхода **Infrastructure as Code (IaC)**.
Проект эмулирует реальную On-Premise инсталляцию: от создания VM на VirtualBox до автоматического деплоя микросервисов через CI/CD.

---

## Архитектура

Проект состоит из **3 виртуальных машин** (Ubuntu Server), управляемых Vagrant и настраиваемых через Ansible.

| Нода | Роль | Ресурсы | Описание |
|------|------|---------|----------|
| **k8s-master** | Control Plane | 8GB RAM, 2 CPU | API Server, Ansible Controller, Helm, CI/CD Runner, Monitoring |
| **k8s-worker-1** | Worker | 4GB RAM, 2 CPU | Запуск нагрузок (Pods) |
| **k8s-worker-2** | Worker | 4GB RAM, 2 CPU | Запуск нагрузок (Pods) |

### Технологический стек
*   **Виртуализация:** VirtualBox + Vagrant
*   **Config Management:** Ansible (автоматическая установка Docker, Kubeadm, Helm, Network)
*   **Container Runtime:** Containerd (с включенным SystemdCgroup)
*   **Orchestration:** Kubernetes v1.34 (Kubeadm)
*   **Network (CNI):** Flannel
*   **CI/CD:** GitLab CI + Remote Runner (внутри кластера) + Kaniko (сборка без Docker-in-Docker)
*   **Monitoring:** Prometheus Operator + Grafana + Node Exporter
*   **App:** Python Flask + Redis (Microservices pattern)

---

## Быстрый старт

### Требования
*   Windows / macOS / Linux
*   Установленные **VirtualBox** и **Vagrant**
*   Минимум 16GB RAM на хост-машине

### Установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/All2Enable/k8s-petproject.git
    cd k8s-project
    ```

2.  **Настройка токена GitLab CI (Обязательно):**
    Для работы автоматического деплоя необходимо зарегистрировать Runner.
    *   Создайте проект в GitLab.
    *   Зайдите в `Settings` -> `CI/CD` -> `Runners` -> `New Project Runner`.
    *   Тэги: `local-k8s`.
    *   Скопируйте токен (начинается с `glrt-...`).
    *   Откройте файл `ansible/roles/gitlab-runner/tasks/main.yml`.
    *   Вставьте токен в строку: `--set runnerToken="ВАШ_ТОКЕН"`.

3.  **Запуск инфраструктуры:**
    Одной командой поднимаем VMs, настраиваем сеть и устанавливаем весь софт:
    ```bash
    vagrant up
    ```
    *Процесс займет 10-20 минут в зависимости от скорости интернета.*

---

## Доступ к сервисам

После успешного развертывания сервисы доступны с хост-машины по следующим адресам:

| Сервис | Адрес | Описание | Логин/Пароль |
|--------|-------|----------|--------------|
| **Web App** | [http://192.168.56.10:30001](http://192.168.56.10:30001) | Demo Python App | - |
| **Grafana** | [http://192.168.56.10:30002](http://192.168.56.10:30002) | Мониторинг кластера | `admin` / (см. ниже) |
| **Prometheus**| [http://192.168.56.10:30003](http://192.168.56.10:30003) | Метрики | - |

### Как узнать пароль от Grafana
Пароль генерируется автоматически. Чтобы узнать его, выполните команду на мастере:
```bash
vagrant ssh master
kubectl get secret --namespace monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

## CI/CD Pipeline

Проект настроен как **Монорепозиторий**.
При пуше изменений в ветку `master` на GitLab автоматически запускается пайплайн:

1.  **Build:** GitLab Runner (внутри K8s) запускает **Kaniko**.
2.  Kaniko собирает Docker-образ и пушит его во внутренний **GitLab Container Registry**.
3.  **Deploy:** Runner обновляет Deployment в кластере.
4.  Если база данных (Redis) отсутствует, она создается автоматически.

---

## Структура проекта

```text
.
├── Vagrantfile             # Описание виртуальных машин
├── ansible/                # Ansible Playbooks и Роли
│   ├── roles/              
│   │   ├── docker/         # Установка Docker/Containerd
│   │   ├── k8s-install/    # Установка kubeadm, kubectl
│   │   ├── k8s-master/     # Инициализация Control Plane
│   │   ├── k8s-worker/     # Джойн воркеров
│   │   ├── helm/           # Установка Helm
│   │   ├── gitlab-runner/  # Установка Runner через Helm Chart
│   │   └── monitoring/     # Развертывание Prometheus Stack
│   └── playbook.yml        # Главный сценарий
├── app/                    # Исходный код приложения
│   ├── k8s/                # Kubernetes манифесты (App + Redis)
│   ├── app.py              # Flask приложение
│   └── Dockerfile          # Инструкция сборки
└── .gitlab-ci.yml          # Описание CI/CD пайплайна
```


---

## Безопасность

*   В репозитории **нет** SSH-ключей (они генерируются локально Vagrant'ом).
*   В репозитории **нет** активных токенов (используются заглушки).
*   Секреты для доступа к Registry создаются динамически в CI/CD.

---

### Автор
All2Enable
```