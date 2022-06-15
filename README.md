# Altic

Создание пакетов безо всякой боли с использованием всего одной команды.

## Команды

- altic new - создать новый пакет в интерактивном режиме
- altic build - собрать текущий пакет
- altic rebuild - пересобрать текущий пакет
- altic deploy - отправить текущий пакет в репозиторий
- altic shell - войти внутрь хэшера для отладки

> В команды build, rebuild и shell можно передавать внутренние параметры для аналогичных команд Hasher

## Конфиг
Находится в `~/.local/altic/config.yml`, представяет собой YAML-файл со следующим содержанием:
```yaml
# Cписок песочниц, их может быть сколько угодно
sandboxes:
  - root: /home/thealchemist/repo/  # корень песочницы
    hasher: /home/thealchemist/.hasher/  # место хранения конфигов Hasher
    arch: x86_64  # архитектура песочницы
    mountpoints:  # устройства, которые монтируются в песочницу
      - /proc
      - /dev/pts
      - /sys
    build:  # настройки сборки
      nprocs: 2  # количество процессов сборки
    gear: true  # используется ли Gear

infrastructure:  # настройки инфраструктуры
  ssh_gitery_hostname: git.alt  # ваш алиас гитери в .ssh/config
  ssh_gyle_hostname: gyle.alt  # ваш алиас гила в .ssh/config
```

## Установка
`pip install git+https://github.com/atthealchemist/altic.git`
