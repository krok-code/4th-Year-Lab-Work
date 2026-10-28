# Command: create-actions

## Description

Викликає skill `github-actions` для генерації кросплатформного CI workflow[cite: 6, 7, 8].

## Prerequisites

- Готовий проєкт із налаштованими тестами[cite: 5, 6, 7].

## Actions

1. Створити локальні скрипти запуску `scripts/ci.sh` та `scripts/ci.bat`[cite: 7].
2. Створити файл конфігурації `.github/workflows/ci.yml` з матрицею ОС (Ubuntu, Windows, macOS)[cite: 4, 6, 7, 8].

## Verification

- Синтаксис YAML є валідним[cite: 8].
- CI Workflow запускається при push та pull_request[cite: 8].
