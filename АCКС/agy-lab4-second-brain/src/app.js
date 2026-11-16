/**
 * Local-First Second Brain Application
 * Pure Vanilla JavaScript - 100% Offline, Zero-Dependency, No-Server Required
 * Works directly by opening index.html in any modern browser via file:///
 */

// 1. Початковий набір 8 навчальних нотаток за темами: Архітектура КС, Linux, Хмари, ШІ
const INITIAL_NOTES = [
  {
    id: "note-1",
    filename: "MOC - Комп'ютерні системи, Хмари та Штучний Інтелект.md",
    category: "Areas",
    title: "MOC - Комп'ютерні системи, Хмари та Штучний Інтелект",
    created: "2026-11-16 11:40:00",
    updated: "2026-11-16 11:40:00",
    tags: ["moc", "архітектура", "linux", "хмари", "штучний-інтелект"],
    status: "active",
    type: "area",
    source: "навчальна програма дисциплін КС, ОС та хмарних обчислень",
    content: `## Короткий зміст
Оглядова карта знань (Map of Content), яка систематизує концепції апаратної архітектури сучасних обчислювальних систем, механізмів ядра Linux, хмарної контейнеризації та апаратного прискорення алгоритмів штучного інтелекту.

## Основні твердження
- Архітектура комп'ютерних систем формує фундамент продуктивності через організацію ієрархії пам'яті та взаємодію між процесором і прискорювачами.
- Операційна система Linux виступає базовим середовищем виконання завдяки низькорівневим механізмам ізоляції та розподілу ресурсів.
- Хмарні платформи та контейнеризація масштабують системні абстракції на рівень розподілених кластерів.
- Сучасні робочі навантаження ШІ вимагають тісної інтеграції спеціалізованого заліза (GPU/TPU/NPU), операційної системи та хмарної інфраструктури оркестрації.

## Пов'язані нотатки
- [[Ієрархія пам'яті та когерентність кешів CPU]]
- [[Ізоляція процесів у Linux - Namespaces та Cgroups]]
- [[Контейнеризація та мікросервісна архітектура]]
- [[Розгортання Kubernetes-кластера для інференсу ШІ]]
- [[Апаратні прискорювачі ШІ - GPU, TPU та NPU]]
- [[Локальне розгортання LLM за допомогою Ollama]]
- [[Міграція монолітної системи в хмару AWS]]`
  },
  {
    id: "note-2",
    filename: "Локальне розгортання LLM за допомогою Ollama.md",
    category: "Inbox",
    title: "Локальне розгортання LLM за допомогою Ollama",
    created: "2026-11-16 11:41:00",
    updated: "2026-11-16 11:41:00",
    tags: ["штучний-інтелект", "llm", "локальний-сервер", "inbox"],
    status: "draft",
    type: "fleeting",
    source: "дослідження документації Ollama та llama.cpp",
    content: `## Короткий зміст
Попередня чернетка з тестування локального середовища виконання великих мовних моделей (LLM) через Ollama для забезпечення приватності даних та автономної роботи без сторонніх хмарних API.

## Основні твердження
- Ollama базується на оптимізованому рушії llama.cpp і підтримує 4-бітне та 8-бітне квантування ваг (GGUF), що зменшує вимоги до VRAM.
- Локальний запуск моделі Llama 3 8B або Mistral 7B можливий на споживчих GPU з 8-12 ГБ VRAM без значної деградації якості відповідей.
- Необхідно дослідити продуктивність інференсу при паралельному навантаженні та інтегрувати сервіс у проєктний кластер.

## Пов'язані нотатки
- [[Апаратні прискорювачі ШІ - GPU, TPU та NPU]]
- [[Розгортання Kubernetes-кластера для інференсу ШІ]]
- [[MOC - Комп'ютерні системи, Хмари та Штучний Інтелект]]`
  },
  {
    id: "note-3",
    filename: "Розгортання Kubernetes-кластера для інференсу ШІ.md",
    category: "Projects",
    title: "Розгортання Kubernetes-кластера для інференсу ШІ",
    created: "2026-11-16 11:42:00",
    updated: "2026-11-16 11:42:00",
    tags: ["проєкт", "kubernetes", "хмари", "штучний-інтелект", "devops"],
    status: "active",
    type: "project",
    source: "курсовий інженерний проєкт",
    content: `## Короткий зміст
Проєкт створення відмовостійкого локально-хмарного Kubernetes-кластера з підтримкою NVIDIA GPU Operator для динамічного масштабування та оркестрації мікросервісів генеративного ШІ.

## Основні твердження
- Кластер використовує K3s як легковажний дистрибутив Kubernetes для мінімізації накладних витрат майстер-вузла.
- Інтеграція NVIDIA Container Toolkit дозволяє подам (Pods) отримувати прямий доступ до апаратних ресурсів відеокарти через cgroups v2.
- Застосовується механізм Horizontal Pod Autoscaler (HPA) на базі кастомних метрик черги запитів інференсу.

## Пов'язані нотатки
- [[Контейнеризація та мікросервісна архітектура]]
- [[Ізоляція процесів у Linux - Namespaces та Cgroups]]
- [[Апаратні прискорювачі ШІ - GPU, TPU та NPU]]
- [[Локальне розгортання LLM за допомогою Ollama]]
- [[MOC - Комп'ютерні системи, Хмари та Штучний Інтелект]]`
  },
  {
    id: "note-4",
    filename: "Міграція монолітної системи в хмару AWS.md",
    category: "Archives",
    title: "Міграція монолітної системи в хмару AWS",
    created: "2026-09-10 09:00:00",
    updated: "2026-10-15 17:30:00",
    tags: ["архів", "aws", "хмари", "міграція", "devops"],
    status: "archived",
    type: "archive",
    source: "завершений виробничий кейс та навчальний звіт",
    content: `## Короткий зміст
Підсумковий звіт та документація процесу міграції застарілого монолітного застосунку з локальної фізичної інфраструктури у публічну хмару AWS з використанням патерну Strangler Fig.

## Основні твердження
- Початковий етап Rehosting (Lift and Shift) дозволив швидко зупинити витрати на підтримку локальних фізичних серверів.
- Подальший рефакторинг розбив моноліт на незалежні сервіси, запаковані в Docker-контейнери під керуванням AWS ECS Fargate.
- База даних переведена на керований сервіс Amazon RDS Multi-AZ, що забезпечило доступність на рівні 99.95% та автоматичні бекапи.

## Пов'язані нотатки
- [[Контейнеризація та мікросервісна архітектура]]
- [[MOC - Комп'ютерні системи, Хмари та Штучний Інтелект]]`
  },
  {
    id: "note-5",
    filename: "Ізоляція процесів у Linux - Namespaces та Cgroups.md",
    category: "Resources",
    title: "Ізоляція процесів у Linux - Namespaces та Cgroups",
    created: "2026-11-16 11:43:00",
    updated: "2026-11-16 11:43:00",
    tags: ["linux", "ядро", "ізоляція", "контейнери", "безпека"],
    status: "active",
    type: "resource",
    source: "Kerrisk M. The Linux Programming Interface",
    content: `## Короткий зміст
Фундаментальні механізми ядра Linux (Namespaces та Control Groups), які забезпечують ізоляцію системних ресурсів і є базовою технологією функціонування сучасних контейнерних рушіїв.

## Основні твердження
- Linux Namespaces ізолюють видимість системних ресурсів: PID (ідентифікатори процесів), NET (мережеві інтерфейси), MNT (точки монтування), IPC, UTS та USER.
- Control Groups (cgroups v2) відповідають за облік, обмеження та пріоритизацію використання апаратних ресурсів (CPU, пам'ять, I/O диска, pids).
- Об'єднання просторів імен, cgroups та обмежень seccomp/capabilities створює безпечне середовище виконання без накладних витрат повної апаратної емуляції гіпервізора.

## Пов'язані нотатки
- [[Контейнеризація та мікросервісна архітектура]]
- [[Розгортання Kubernetes-кластера для інференсу ШІ]]
- [[MOC - Комп'ютерні системи, Хмари та Штучний Інтелект]]`
  },
  {
    id: "note-6",
    filename: "Контейнеризація та мікросервісна архітектура.md",
    category: "Resources",
    title: "Контейнеризація та мікросервісна архітектура",
    created: "2026-11-16 11:44:00",
    updated: "2026-11-16 11:44:00",
    tags: ["хмари", "контейнери", "docker", "мікросервіси", "архітектура"],
    status: "active",
    type: "resource",
    source: "Newman S. Building Microservices",
    content: `## Короткий зміст
Концепція розробки та пакування програмного забезпечення у стандартизовані контейнерні образи (OCI), що дозволяє будувати масштабовані розподілені мікросервісні системи.

## Основні твердження
- Контейнеризація не є віртуалізацією обладнання; вона використовує ядро хоста та спирається на [[Ізоляція процесів у Linux - Namespaces та Cgroups]].
- Мікросервісна архітектура забезпечує незалежний життєвий цикл релізів, окреме масштабування компонентів та ізоляцію відмов між доменами.
- Декларативне керування через OCI runtime (runc, containerd) гарантує ідентичність середовища розробки та промислового кластера.

## Пов'язані нотатки
- [[Ізоляція процесів у Linux - Namespaces та Cgroups]]
- [[Розгортання Kubernetes-кластера для інференсу ШІ]]
- [[Міграція монолітної системи в хмару AWS]]
- [[MOC - Комп'ютерні системи, Хмари та Штучний Інтелект]]`
  },
  {
    id: "note-7",
    filename: "Ієрархія пам'яті та когерентність кешів CPU.md",
    category: "Resources",
    title: "Ієрархія пам'яті та когерентність кешів CPU",
    created: "2026-11-16 11:45:00",
    updated: "2026-11-16 11:45:00",
    tags: ["архітектура", "пам'ять", "cpu", "кеш", "mesi"],
    status: "active",
    type: "resource",
    source: "Hennessy & Patterson. Computer Architecture: A Quantitative Approach",
    content: `## Короткий зміст
Огляд багаторівневої ієрархії пам'яті в сучасних суперскалярних процесорах, вплив просторової та часової локальності на продуктивність і протоколи когерентності кеш-пам'яті в SMP-системах.

## Основні твердження
- Ієрархія пам'яті (регістри -> L1 -> L2 -> L3 -> RAM -> NVMe) покликана приховати затримку звернення (Memory Wall) за рахунок принципів часової та просторової локальності даних.
- У симетричних мультипроцесорних системах (SMP) протоколи когерентності (наприклад, MESI/MOESI) запобігають ситуаціям читання застарілих даних різними ядрами.
- Розуміння лінійки кешу (зазвичай 64 байти) є критичним для уникнення феномену помилкового спільного використання (False Sharing) у багатопотокових обчисленнях.

## Пов'язані нотатки
- [[Апаратні прискорювачі ШІ - GPU, TPU та NPU]]
- [[MOC - Комп'ютерні системи, Хмари та Штучний Інтелект]]`
  },
  {
    id: "note-8",
    filename: "Апаратні прискорювачі ШІ - GPU, TPU та NPU.md",
    category: "Resources",
    title: "Апаратні прискорювачі ШІ - GPU, TPU та NPU",
    created: "2026-11-16 11:46:00",
    updated: "2026-11-16 11:46:00",
    tags: ["штучний-інтелект", "апаратне-забезпечення", "gpu", "tpu", "прискорювачі"],
    status: "active",
    type: "resource",
    source: "Jouppi N. et al. A Domain-Specific Architecture for Deep Neural Networks",
    content: `## Короткий зміст
Аналіз спеціалізованих апаратних архітектур (Domain-Specific Architectures — DSA), оптимізованих для паралельного виконання операцій множення матриць (GEMM) та тензорних обчислень у нейронних мережах.

## Основні твердження
- На відміну від універсальних CPU, орієнтованих на низьку затримку одиночних потоків, GPU максимізують сумарну пропускну здатність через масивний паралелізм (SIMT/SIMD).
- Google TPU використовує систолічні масиви (Systolic Arrays), де дані передаються безпосередньо між сусідніми обчислювальними елементами без повторних звернень до регістрового файлу, що кардинально знижує енергоспоживання.
- NPU (Neural Processing Units) вбудовуються в мобільні SoC та ноутбуки для енергоефективного виконання локальних інференс-моделей квантованого формату (INT8/INT4).

## Пов'язані нотатки
- [[Ієрархія пам'яті та когерентність кешів CPU]]
- [[Локальне розгортання LLM за допомогою Ollama]]
- [[Розгортання Kubernetes-кластера для інференсу ШІ]]
- [[MOC - Комп'ютерні системи, Хмари та Штучний Інтелект]]`
  }
];

// 2. Головний контролер застосунку
class SecondBrainApp {
  constructor() {
    this.notes = this.loadNotes();
    this.currentCategory = "ALL";
    this.activeTag = null;
    this.searchQuery = "";
    this.selectedNoteId = this.notes.length > 0 ? this.notes[0].id : null;

    this.initDOM();
    this.bindEvents();
    this.render();
  }

  // Завантаження нотаток (з LocalStorage або дефолтного набору)
  loadNotes() {
    try {
      const stored = localStorage.getItem("second_brain_notes");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn("Помилка читання localStorage, використовується початковий набір нотаток:", e);
    }
    return JSON.parse(JSON.stringify(INITIAL_NOTES));
  }

  // Збереження в LocalStorage
  saveNotes() {
    try {
      localStorage.setItem("second_brain_notes", JSON.stringify(this.notes));
    } catch (e) {
      console.error("Не вдалося зберегти нотатки в localStorage:", e);
    }
  }

  // Ініціалізація DOM посилань
  initDOM() {
    this.dom = {
      searchInput: document.getElementById("searchInput"),
      clearSearchBtn: document.getElementById("clearSearchBtn"),
      importFolderInput: document.getElementById("importFolderInput"),
      importFilesInput: document.getElementById("importFilesInput"),
      importBtn: document.getElementById("importBtn"),
      newNoteBtn: document.getElementById("newNoteBtn"),
      resetToDefaultBtn: document.getElementById("resetToDefaultBtn"),
      categoryButtons: document.querySelectorAll(".category-nav .nav-item"),
      tagCloud: document.getElementById("tagCloud"),
      resetTagBtn: document.getElementById("resetTagBtn"),
      currentCategoryLabel: document.getElementById("currentCategoryLabel"),
      activeTagBadge: document.getElementById("activeTagBadge"),
      notesCountInfo: document.getElementById("notesCountInfo"),
      notesList: document.getElementById("notesList"),
      emptyState: document.getElementById("emptyState"),
      emptyStateMsg: document.getElementById("emptyStateMsg"),
      resetFiltersBtn: document.getElementById("resetFiltersBtn"),
      noteViewer: document.getElementById("noteViewer"),
      noNoteSelected: document.getElementById("noNoteSelected"),
      viewTitle: document.getElementById("viewTitle"),
      viewCategoryBadge: document.getElementById("viewCategoryBadge"),
      viewStatusBadge: document.getElementById("viewStatusBadge"),
      viewTypeBadge: document.getElementById("viewTypeBadge"),
      viewDate: document.getElementById("viewDate"),
      viewTags: document.getElementById("viewTags"),
      viewSource: document.getElementById("viewSource"),
      viewContent: document.getElementById("viewContent"),
      backlinksSection: document.getElementById("backlinksSection"),
      backlinksList: document.getElementById("backlinksList"),
      // Модальне вікно нової нотатки
      newNoteModal: document.getElementById("newNoteModal"),
      newNoteForm: document.getElementById("newNoteForm"),
      closeModalBtn: document.getElementById("closeModalBtn"),
      cancelModalBtn: document.getElementById("cancelModalBtn"),
      downloadMdBtn: document.getElementById("downloadMdBtn"),
      noteTitleInput: document.getElementById("noteTitleInput"),
      noteCategorySelect: document.getElementById("noteCategorySelect"),
      noteTypeSelect: document.getElementById("noteTypeSelect"),
      noteStatusSelect: document.getElementById("noteStatusSelect"),
      noteTagsInput: document.getElementById("noteTagsInput"),
      noteSourceInput: document.getElementById("noteSourceInput"),
      noteSummaryInput: document.getElementById("noteSummaryInput"),
      notePointsInput: document.getElementById("notePointsInput"),
      noteLinksInput: document.getElementById("noteLinksInput")
    };
  }

  // Прив'язка подій
  bindEvents() {
    // 1. Повнотекстовий пошук
    this.dom.searchInput.addEventListener("input", (e) => {
      this.searchQuery = e.target.value.trim().toLowerCase();
      this.dom.clearSearchBtn.classList.toggle("hidden", !this.searchQuery);
      this.renderNotesList();
    });

    this.dom.clearSearchBtn.addEventListener("click", () => {
      this.dom.searchInput.value = "";
      this.searchQuery = "";
      this.dom.clearSearchBtn.classList.add("hidden");
      this.renderNotesList();
    });

    // 2. Фільтрація за категоріями PARA
    this.dom.categoryButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        this.dom.categoryButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.currentCategory = btn.dataset.category;
        this.renderNotesList();
      });
    });

    // 3. Скидання активного тегу
    this.dom.resetTagBtn.addEventListener("click", () => {
      this.activeTag = null;
      this.renderNotesList();
      this.renderTags();
    });

    // 4. Скидання фільтрів при порожньому пошуку
    this.dom.resetFiltersBtn.addEventListener("click", () => {
      this.currentCategory = "ALL";
      this.activeTag = null;
      this.searchQuery = "";
      this.dom.searchInput.value = "";
      this.dom.clearSearchBtn.classList.add("hidden");
      this.dom.categoryButtons.forEach(b => {
        b.classList.toggle("active", b.dataset.category === "ALL");
      });
      this.render();
    });

    // 5. Кнопка «Завантажити .md файли з папки notes/»
    this.dom.importBtn.addEventListener("click", () => {
      // Пріоритет вибору папки, або мультифайловий вибір
      if (this.dom.importFolderInput) {
        this.dom.importFolderInput.click();
      } else if (this.dom.importFilesInput) {
        this.dom.importFilesInput.click();
      }
    });

    this.dom.importFolderInput.addEventListener("change", (e) => this.handleFileImport(e.target.files));
    this.dom.importFilesInput.addEventListener("change", (e) => this.handleFileImport(e.target.files));

    // Drag and Drop файлів/папок прямо у вікно браузера
    window.addEventListener("dragover", (e) => e.preventDefault());
    window.addEventListener("drop", async (e) => {
      e.preventDefault();
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        await this.handleFileImport(e.dataTransfer.files);
      }
    });

    // 6. Скидання до 8 базових нотаток
    if (this.dom.resetToDefaultBtn) {
      this.dom.resetToDefaultBtn.addEventListener("click", () => {
        if (confirm("Відновити 8 базових навчальних нотаток?")) {
          localStorage.removeItem("second_brain_notes");
          this.notes = JSON.parse(JSON.stringify(INITIAL_NOTES));
          this.currentCategory = "ALL";
          this.activeTag = null;
          this.searchQuery = "";
          this.selectedNoteId = this.notes[0].id;
          this.dom.categoryButtons.forEach(b => b.classList.toggle("active", b.dataset.category === "ALL"));
          this.render();
        }
      });
    }

    // 7. Модальне вікно нової нотатки
    this.dom.newNoteBtn.addEventListener("click", () => this.openNewNoteModal());
    this.dom.closeModalBtn.addEventListener("click", () => this.closeNewNoteModal());
    this.dom.cancelModalBtn.addEventListener("click", () => this.closeNewNoteModal());

    this.dom.newNoteForm.addEventListener("submit", (e) => {
      e.preventDefault();
      this.createNoteFromForm();
    });

    this.dom.downloadMdBtn.addEventListener("click", () => {
      this.downloadNoteAsMarkdown();
    });

    // 8. Клік по внутрішніх посиланнях [[Назва нотатки]]
    document.addEventListener("click", (e) => {
      const wikilink = e.target.closest(".wikilink");
      if (wikilink) {
        e.preventDefault();
        const targetTitle = wikilink.dataset.target;
        this.selectNoteByTitle(targetTitle);
      }
    });
  }

  // Обробка імпорту локальних .md файлів з диска
  async handleFileImport(fileList) {
    if (!fileList || fileList.length === 0) return;

    let importedCount = 0;
    const files = Array.from(fileList).filter(f => f.name.endsWith(".md") || f.name.endsWith(".markdown"));

    for (const file of files) {
      try {
        const text = await file.text();
        const parsed = this.parseMarkdownFile(text, file.name, file.webkitRelativePath || "");
        if (parsed) {
          const existingIdx = this.notes.findIndex(n => n.title.trim().toLowerCase() === parsed.title.trim().toLowerCase());
          if (existingIdx >= 0) {
            this.notes[existingIdx] = { ...this.notes[existingIdx], ...parsed };
          } else {
            this.notes.unshift(parsed);
          }
          importedCount++;
        }
      } catch (err) {
        console.error(`Помилка читання файлу ${file.name}:`, err);
      }
    }

    if (importedCount > 0) {
      this.saveNotes();
      this.selectedNoteId = this.notes[0].id;
      this.render();
      alert(`✅ Успішно зчитано ${importedCount} .md файлів з диска!`);
    } else {
      alert("У вибраному каталозі не знайдено .md файлів.");
    }
  }

  // Парсер вмісту файлу з YAML Frontmatter
  parseMarkdownFile(rawContent, filename, relativePath = "") {
    let category = "Inbox";

    // 1. Спроба витягти категорію зі шляху: notes/Inbox/..., Projects/... тощо
    if (relativePath) {
      const match = relativePath.match(/(?:notes[/\\])?(Inbox|Projects|Areas|Resources|Archives)/i);
      if (match) {
        const found = match[1].toLowerCase();
        category = found.charAt(0).toUpperCase() + found.slice(1);
      }
    }

    const frontmatterRegex = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/;
    const match = rawContent.match(frontmatterRegex);

    let metadata = {};
    let content = rawContent;

    if (match) {
      const yamlBlock = match[1];
      content = match[2].trim();

      const lines = yamlBlock.split("\n");
      let currentArrayKey = null;

      lines.forEach(line => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#")) return;

        if (trimmed.startsWith("- ") && currentArrayKey) {
          const val = trimmed.substring(2).trim().replace(/^['"]|['"]$/g, "");
          if (!Array.isArray(metadata[currentArrayKey])) metadata[currentArrayKey] = [];
          metadata[currentArrayKey].push(val);
          return;
        }

        const colonIdx = trimmed.indexOf(":");
        if (colonIdx > 0) {
          const key = trimmed.substring(0, colonIdx).trim();
          let value = trimmed.substring(colonIdx + 1).trim();

          if (value === "") {
            currentArrayKey = key;
            metadata[key] = [];
          } else {
            currentArrayKey = null;
            if (value.startsWith("[") && value.endsWith("]")) {
              metadata[key] = value.slice(1, -1).split(",").map(s => s.trim().replace(/^['"]|['"]$/g, ""));
            } else {
              metadata[key] = value.replace(/^['"]|['"]$/g, "");
            }
          }
        }
      });
    }

    // 2. Якщо шлях не дав категорію, перевіряємо метадані або тип
    if (metadata.category) {
      const cat = metadata.category.toLowerCase();
      const valid = ["inbox", "projects", "areas", "resources", "archives"];
      if (valid.includes(cat)) {
        category = cat.charAt(0).toUpperCase() + cat.slice(1);
      }
    } else if (category === "Inbox" && metadata.type) {
      const t = metadata.type.toLowerCase();
      if (t === "project") category = "Projects";
      else if (t === "area" || t === "moc") category = "Areas";
      else if (t === "resource") category = "Resources";
      else if (t === "archive") category = "Archives";
    }

    const defaultTitle = filename.replace(/\.(md|markdown)$/i, "");
    const title = metadata.title || defaultTitle;
    const now = new Date().toISOString().replace("T", " ").substring(0, 19);

    return {
      id: "note-" + Math.random().toString(36).substr(2, 9),
      filename: filename,
      category: category,
      title: title,
      created: metadata.created || now,
      updated: metadata.updated || now,
      tags: Array.isArray(metadata.tags) ? metadata.tags : (metadata.tags ? [metadata.tags] : []),
      status: metadata.status || "active",
      type: metadata.type || "resource",
      source: metadata.source || "імпортовано з диска",
      content: content
    };
  }

  // Рендеринг всього інтерфейсу
  render() {
    this.updateCategoryCounters();
    this.renderTags();
    this.renderNotesList();
    this.renderSelectedNote();
  }

  // Оновлення лічильників PARA
  updateCategoryCounters() {
    const counts = {
      ALL: this.notes.length,
      Inbox: 0,
      Projects: 0,
      Areas: 0,
      Resources: 0,
      Archives: 0
    };

    this.notes.forEach(note => {
      if (counts[note.category] !== undefined) {
        counts[note.category]++;
      }
    });

    Object.keys(counts).forEach(cat => {
      const el = document.getElementById(`count-${cat}`);
      if (el) el.textContent = counts[cat];
    });
  }

  // Рендеринг хмари тегів
  renderTags() {
    const tagMap = {};
    this.notes.forEach(n => {
      (n.tags || []).forEach(t => {
        tagMap[t] = (tagMap[t] || 0) + 1;
      });
    });

    const sortedTags = Object.keys(tagMap).sort((a, b) => tagMap[b] - tagMap[a]);
    this.dom.tagCloud.innerHTML = "";

    sortedTags.forEach(tag => {
      const pill = document.createElement("button");
      pill.className = `tag-pill ${this.activeTag === tag ? "active" : ""}`;
      pill.textContent = `#${tag} (${tagMap[tag]})`;
      pill.addEventListener("click", () => {
        this.activeTag = this.activeTag === tag ? null : tag;
        this.renderTags();
        this.renderNotesList();
      });
      this.dom.tagCloud.appendChild(pill);
    });

    this.dom.resetTagBtn.classList.toggle("hidden", !this.activeTag);
    if (this.activeTag) {
      this.dom.activeTagBadge.textContent = `#${this.activeTag}`;
      this.dom.activeTagBadge.classList.remove("hidden");
    } else {
      this.dom.activeTagBadge.classList.add("hidden");
    }
  }

  // Фільтрація нотаток
  getFilteredNotes() {
    return this.notes.filter(note => {
      // 1. Категорія PARA
      if (this.currentCategory !== "ALL" && note.category !== this.currentCategory) {
        return false;
      }
      // 2. Тег
      if (this.activeTag && (!note.tags || !note.tags.includes(this.activeTag))) {
        return false;
      }
      // 3. Повнотекстовий пошук
      if (this.searchQuery) {
        const titleMatch = note.title.toLowerCase().includes(this.searchQuery);
        const contentMatch = (note.content || "").toLowerCase().includes(this.searchQuery);
        const tagsMatch = (note.tags || []).some(t => t.toLowerCase().includes(this.searchQuery));
        const sourceMatch = (note.source || "").toLowerCase().includes(this.searchQuery);
        return titleMatch || contentMatch || tagsMatch || sourceMatch;
      }
      return true;
    });
  }

  // Рендеринг карток списку нотаток
  renderNotesList() {
    const filtered = this.getFilteredNotes();

    this.dom.currentCategoryLabel.textContent = this.currentCategory === "ALL" 
      ? "Всі нотатки" 
      : `${this.currentCategory} (${filtered.length})`;

    this.dom.notesCountInfo.textContent = `${filtered.length} з ${this.notes.length}`;

    // Якщо нічого не знайдено - виведення повідомлення Empty State
    if (filtered.length === 0) {
      this.dom.notesList.innerHTML = "";
      this.dom.emptyState.classList.remove("hidden");
      if (this.searchQuery) {
        this.dom.emptyStateMsg.textContent = `За запитом "${this.searchQuery}" не знайдено жодної нотатки. Спробуйте змінити пошукове слово або скиньте фільтри.`;
      } else if (this.activeTag) {
        this.dom.emptyStateMsg.textContent = `У категорії "${this.currentCategory}" немає нотаток із тегом #${this.activeTag}.`;
      } else {
        this.dom.emptyStateMsg.textContent = `У категорії "${this.currentCategory}" наразі немає нотаток. Створіть нову за допомогою кнопки вгорі.`;
      }
      return;
    }

    this.dom.emptyState.classList.add("hidden");
    this.dom.notesList.innerHTML = "";

    filtered.forEach(note => {
      const card = document.createElement("div");
      card.className = `note-card ${this.selectedNoteId === note.id ? "active" : ""}`;
      card.dataset.id = note.id;

      // Отримання прев'ю з першого розділу
      const summaryMatch = note.content.match(/## Короткий зміст\s+([\s\S]*?)(?=##|$)/);
      const summaryText = summaryMatch ? summaryMatch[1].trim() : (note.content.substring(0, 100) + "...");

      card.innerHTML = `
        <div class="note-card-header">
          <h4 class="note-card-title">${this.escapeHtml(note.title)}</h4>
          <span class="badge-category-mini category-${note.category}">${note.category}</span>
        </div>
        <p class="note-card-summary">${this.escapeHtml(summaryText)}</p>
        <div class="note-card-footer">
          <div class="card-tags">
            ${(note.tags || []).slice(0, 3).map(t => `<span class="card-tag">#${this.escapeHtml(t)}</span>`).join("")}
          </div>
          <span class="card-date">${note.updated.substring(0, 10)}</span>
        </div>
      `;

      card.addEventListener("click", () => {
        this.selectedNoteId = note.id;
        this.renderNotesList();
        this.renderSelectedNote();
      });

      this.dom.notesList.appendChild(card);
    });

    // Якщо вибрана нотатка випала з результатів фільтру
    if (!filtered.some(n => n.id === this.selectedNoteId)) {
      this.selectedNoteId = filtered[0].id;
      this.renderSelectedNote();
    }
  }

  // Рендеринг перегляду обраної нотатки
  renderSelectedNote() {
    const note = this.notes.find(n => n.id === this.selectedNoteId);

    if (!note) {
      this.dom.noteViewer.classList.add("hidden");
      this.dom.noNoteSelected.classList.remove("hidden");
      return;
    }

    this.dom.noNoteSelected.classList.add("hidden");
    this.dom.noteViewer.classList.remove("hidden");

    this.dom.viewTitle.textContent = note.title;
    this.dom.viewCategoryBadge.textContent = note.category;
    this.dom.viewCategoryBadge.className = `badge-category category-${note.category}`;

    this.dom.viewStatusBadge.textContent = note.status || "active";
    this.dom.viewTypeBadge.textContent = note.type || "note";
    this.dom.viewDate.textContent = `Створено: ${note.created} | Оновлено: ${note.updated}`;

    // Теги
    this.dom.viewTags.innerHTML = (note.tags || []).map(t => 
      `<button class="tag-pill" style="border:none" onclick="window.app.filterByTag('${this.escapeHtml(t)}')">#${this.escapeHtml(t)}</button>`
    ).join("");

    // Джерело
    this.dom.viewSource.textContent = note.source ? `Джерело: ${note.source}` : "";

    // Тіло з Markdown та [[Wikilinks]]
    this.dom.viewContent.innerHTML = this.renderMarkdown(note.content || "");

    // Зворотні посилання
    this.renderBacklinks(note.title);
  }

  // Швидкий фільтр за кліком на тег у перегляді
  filterByTag(tag) {
    this.activeTag = tag;
    this.renderTags();
    this.renderNotesList();
  }

  // Обчислення зворотних посилань (Backlinks)
  renderBacklinks(currentTitle) {
    const escapedTitle = currentTitle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(`\\[\\[${escapedTitle}(\\|.*?)?\\]\\]`, "i");

    const referringNotes = this.notes.filter(n => {
      if (n.title.toLowerCase() === currentTitle.toLowerCase()) return false;
      return pattern.test(n.content || "");
    });

    this.dom.backlinksList.innerHTML = "";

    if (referringNotes.length === 0) {
      this.dom.backlinksList.innerHTML = `<span class="no-backlinks">Немає вхідних посилань на цю нотатку.</span>`;
      return;
    }

    referringNotes.forEach(ref => {
      const item = document.createElement("div");
      item.className = "backlink-item";
      item.innerHTML = `
        <span class="backlink-title">🔗 ${this.escapeHtml(ref.title)}</span>
        <span class="backlink-category">${ref.category}</span>
      `;
      item.addEventListener("click", () => {
        this.selectedNoteId = ref.id;
        this.renderNotesList();
        this.renderSelectedNote();
      });
      this.dom.backlinksList.appendChild(item);
    });
  }

  // Навігація за внутрішнім посиланням [[Назва нотатки]]
  selectNoteByTitle(targetTitle) {
    if (!targetTitle) return;
    const cleanTitle = targetTitle.replace(/&#039;|&apos;/g, "'").replace(/[’`]/g, "'").trim().toLowerCase();
    const targetNote = this.notes.find(n => {
      const noteTitle = n.title.replace(/&#039;|&apos;/g, "'").replace(/[’`]/g, "'").trim().toLowerCase();
      return noteTitle === cleanTitle;
    });

    if (targetNote) {
      this.selectedNoteId = targetNote.id;
      // Якщо категорія була відфільтрована, перемикаємо на All або відповідну категорію
      if (this.currentCategory !== "ALL" && this.currentCategory !== targetNote.category) {
        this.currentCategory = "ALL";
        this.dom.categoryButtons.forEach(b => b.classList.toggle("active", b.dataset.category === "ALL"));
      }
      this.activeTag = null;
      this.searchQuery = "";
      this.dom.searchInput.value = "";
      this.dom.clearSearchBtn.classList.add("hidden");
      this.render();
    } else {
      alert(`Нотатку з назвою "[[${targetTitle}]]" не знайдено в базі знань. Ви можете створити її через кнопку "Нова нотатка"!`);
    }
  }

  // Локальний рендерер Markdown з підтримкою [[Wikilinks]]
  renderMarkdown(text) {
    if (!text) return "";

    let html = this.escapeHtml(text);

    // Заміна [[Назва нотатки|Аліас]] та [[Назва нотатки]] на клікабельні елементи
    // Виправляємо баг з апострофом: нормалізуємо &#039; та &apos; назад у коректний апостроф
    html = html.replace(/\[\[(.*?)(?:\|(.*?))?\]\]/g, (match, title, alias) => {
      const cleanTitle = title.replace(/&#039;|&apos;/g, "'").trim();
      const displayText = alias ? alias.replace(/&#039;|&apos;/g, "'").trim() : cleanTitle;
      return `<a href="#" class="wikilink" data-target="${this.escapeHtml(cleanTitle)}">[[${this.escapeHtml(displayText)}]]</a>`;
    });

    // Заголовки: ###, ##, #
    html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    html = html.replace(/^## (.*$)/gim, "<h2>$1</h2>");
    html = html.replace(/^# (.*$)/gim, "<h1>$1</h1>");

    // Жирний текст: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Блоки коду ```...```
    html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");

    // Інлайн код: `...`
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Невпорядковані списки: - пункт
    html = html.replace(/^\- (.*$)/gim, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/gims, "<ul>$1</ul>");
    html = html.replace(/<\/ul>\s*<ul>/g, "");

    // Формули LaTeX: $$...$$ або $...$
    html = html.replace(/\$\$([\s\S]*?)\$\$/g, "<div class='math-display'><code>$1</code></div>");
    html = html.replace(/\$([^\$]+)\$/g, "<code class='math-inline'>$1</code>");

    // Абзаци (подвійні переноси рядків)
    const paragraphs = html.split(/\n\n+/);
    html = paragraphs.map(p => {
      p = p.trim();
      if (!p) return "";
      if (p.startsWith("<h") || p.startsWith("<ul") || p.startsWith("<pre") || p.startsWith("<div")) {
        return p;
      }
      return `<p>${p.replace(/\n/g, "<br>")}</p>`;
    }).join("\n");

    return html;
  }

  // Екранування HTML (безпечне для українського апострофа)
  escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // Відкриття модального вікна
  openNewNoteModal() {
    this.dom.newNoteForm.reset();
    this.dom.noteCategorySelect.value = "Inbox";
    this.dom.noteStatusSelect.value = "draft";
    this.dom.noteTypeSelect.value = "fleeting";
    this.dom.newNoteModal.classList.remove("hidden");
    this.dom.noteTitleInput.focus();
  }

  closeNewNoteModal() {
    this.dom.newNoteModal.classList.add("hidden");
  }

  // Збирання даних з форми створення нотатки
  buildNoteFromForm() {
    const title = this.dom.noteTitleInput.value.trim();
    if (!title) return null;

    const category = this.dom.noteCategorySelect.value || "Inbox";
    const type = this.dom.noteTypeSelect.value || "fleeting";
    const status = this.dom.noteStatusSelect.value || "draft";
    const source = this.dom.noteSourceInput.value.trim() || "власні думки";
    const tags = this.dom.noteTagsInput.value
      .split(",")
      .map(t => t.trim().replace(/^#/, ""))
      .filter(t => t.length > 0);

    const summary = this.dom.noteSummaryInput.value.trim() || "Короткий опис нотатки.";
    let points = this.dom.notePointsInput.value.trim();
    if (!points) {
      points = "- Ключова теза або спостереження";
    } else {
      points = points.split("\n").map(l => l.trim().startsWith("- ") ? l.trim() : `- ${l.trim()}`).join("\n");
    }

    let links = this.dom.noteLinksInput.value.trim();
    if (!links) {
      links = "- Немає посилань";
    } else {
      links = links.split(",").map(l => {
        let clean = l.trim();
        if (!clean.startsWith("[[")) clean = `[[${clean}]]`;
        return `- ${clean}`;
      }).join("\n");
    }

    const now = new Date().toISOString().replace("T", " ").substring(0, 19);

    const content = `## Короткий зміст\n${summary}\n\n## Основні твердження\n${points}\n\n## Пов'язані нотатки\n${links}`;

    const rawMarkdown = `---
title: "${title}"
created: "${now}"
updated: "${now}"
tags:
${tags.map(t => `  - "${t}"`).join("\n")}
status: "${status}"
type: "${type}"
source: "${source}"
---

${content}
`;

    return {
      noteObj: {
        id: "note-" + Date.now(),
        filename: `${title}.md`,
        category: category,
        title: title,
        created: now,
        updated: now,
        tags: tags,
        status: status,
        type: type,
        source: source,
        content: content
      },
      rawMarkdown: rawMarkdown,
      filename: `${title}.md`
    };
  }

  // Створення та збереження нотатки в браузері (localStorage)
  createNoteFromForm() {
    const built = this.buildNoteFromForm();
    if (!built) return;

    this.notes.unshift(built.noteObj);
    this.saveNotes();
    this.selectedNoteId = built.noteObj.id;
    this.closeNewNoteModal();
    this.render();
  }

  // Завантаження згенерованого .md файлу на диск для папки notes/Inbox
  downloadNoteAsMarkdown() {
    const built = this.buildNoteFromForm();
    if (!built) {
      alert("Будь ласка, введіть принаймні назву нотатки.");
      return;
    }

    const blob = new Blob([built.rawMarkdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = built.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    // Також зберігаємо в браузері
    this.createNoteFromForm();
  }
}

// Запуск при завантаженні документа
document.addEventListener("DOMContentLoaded", () => {
  window.app = new SecondBrainApp();
});
