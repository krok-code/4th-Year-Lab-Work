# Архітектура AI-Агента (Build Engineer)

## 1. Назначення та проблеми

AI-агент автоматизує процес розгортання, збірки, тестування та налаштування CI/CD для кросплатформного JavaScript проєкту на базі Jest[cite: 1, 3, 5, 7].

## 2. Компоненти системи

- **Agent Manifest (`build-engineer.agent.md`):** Описує роль, правила безпеки та критерії завершення[cite: 3, 4, 7].
- **Skills (`.github/skills/`):**
  - `project-scaffold` — створення базової структури файлів[cite: 6, 7].
  - `build-and-test` — конфігурація та запуск юніт-тестів[cite: 6, 7].
  - `github-actions` — налаштування автоперевірок на GitHub[cite: 6, 7].
- **Commands (`.github/prompts/`):** Окремі атомарні операції (`git-init`, `create-project`, `create-build`, `create-actions`, `check`)[cite: 5, 6, 7, 8].
- **Orchestrator (`init.prompt.md`):** Керує послідовним викликом команд та обробкою помилок[cite: 4, 6, 8].

## 3. Передавання даних між етапами

1. `git-init` готує репозиторій та `.gitignore`[cite: 3, 5, 8].
2. `create-project` генерує кодову базу `src/index.js`[cite: 6, 7, 8].
3. `create-build` додає `tests/index.test.js` та `package.json`[cite: 5, 6, 7, 8].
4. `create-actions` створює `scripts/` та `.github/workflows/ci.yml`[cite: 6, 7, 8].
5. `check` виконує підсумкову перевірку всіх компонентів[cite: 8].

## 4. Обробка помилок

Якщо будь-яка команда чи тест повертає помилку, оркестратор зупиняє виконання та виводить звіт про збій без внесення незворотних змін[cite: 4, 8].
