# Command: create-build

## Description

Викликає skill `build-and-test` для налаштування тестового середовища Jest та створення юніт-тестів[cite: 5, 6, 7, 8].

## Prerequisites

- Існування файлу `package.json` та модулів проєкту[cite: 5, 6, 7].

## Actions

1. Додати залежність `jest` до `package.json`[cite: 5, 6].
2. Налаштувати тестовий скрипт `jest --runInBand`[cite: 5].
3. Створити тестовий файл `tests/index.test.js`[cite: 5, 6, 8].

## Verification

- Локальний запуск `npm test` успішно виконує тести[cite: 5, 8].
