# Command: git-init

## Description

Перевіряє стан Git-репозиторію, створює або оновлює `.gitignore` та показує поточний статус.

## Prerequisites

- Наявність встановленого Git у системі[cite: 1, 2].

## Actions

1. Перевірити наявність Git-репозиторію (`git status`)[cite: 7, 8].
2. Створити або доповнити `.gitignore` записом `node_modules/`[cite: 3, 5, 6].
3. Вивести поточний стан робочого дерева[cite: 7, 8].

## Verification

- Команда `git status` виконується без помилок[cite: 8].
- Файл `.gitignore` містить необхідні виключення[cite: 3, 5, 7].
