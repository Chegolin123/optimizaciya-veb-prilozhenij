---
tags:
  - учёба
  - конспект
type: lesson
subject: "Оптимизация веб-приложений"
lecture: 33
topic: "DOM дерево"
date: "2026-10-13"
status: active
created: "2026-10-13"
updated: "2026-10-13"
---

# Конспект — DOM дерево

> Занятие 33 (13.10.2026, Рыбаков). Темы DOM нет в таблице курса — занял следующий свободный номер после 32. Материал со слайда «Таблица методов поиска» + разбор DOM в браузере.

## Что такое DOM

**DOM (Document Object Model)** — объектная модель документа: браузер превращает HTML-разметку в **дерево объектов**, доступное из JavaScript. Каждый тег, атрибут и текстовый узел — объект со свойствами, методами и событиями.

```
document
└── html
    ├── head
    │   ├── title
    │   └── meta
    └── body
        ├── h1
        ├── div.card
        │   ├── h2
        │   ├── img
        │   └── button
        └── form
            ├── input
            └── button
```

**Узел (node) бывает:** элемент (`Element`), текстовый (`Text`), комментарий, атрибут, документ (`Document`). Вершина дерева — `document`, входа в `<html>` — `document.documentElement`, `<body>` — `document.body`.

## Типы узлов

Не всё в DOM — теги. У каждого узла свой `nodeType`:

| nodeType | Узел | Пример |
|----------|------|--------|
| 1 | ELEMENT_NODE | `<div>`, `<li>`, `<input>` |
| 3 | TEXT_NODE | текст между тегами (включая пробелы и переносы строк!) |
| 8 | COMMENT_NODE | `<!-- комментарий -->` |
| 9 | DOCUMENT_NODE | сам `document` |
| 10 | DOCTYPE_NODE | `<!DOCTYPE html>` |
| 11 | DOCUMENT_FRAGMENT_NODE | «контейнер без родителя» (см. ниже) |

```js
const card = document.querySelector('.card');
card.nodeType;        // 1 (Element)
card.nodeName;        // 'DIV' — в верхнем регистре для элементов
card.firstChild;       // это скорее всего ТЕКСТОВЫЙ узел (\n  пробелы между тегами), а не <h2>!
```

Ловушка новичка: `firstChild`/`childNodes` возвращают **все** узлы, включая текстовые и пробелы. Если в разметке есть отступы/переносы, они станут `nodeType: 3`. Для работы «только с тегами» есть `children`/`firstElementChild`.

## Навигация по дереву (без селекторов)

### Все узлы (включая текст и комментарии)

| Свойство | Что даёт |
|----------|----------|
| `parentNode` | Родительский узел |
| `childNodes` | Коллекция всех дочерних узлов (список, не массив) |
| `firstChild` / `lastChild` | Первый / последний дочерний узел |
| `nextSibling` / `previousSibling` | Следующий / предыдущий узел на том же уровне |
| `contains(node)` | true, если node — потомок |

### Только элементы

| Свойство | Что даёт |
|----------|----------|
| `parentElement` | Родитель-элемент (не document/не текст) |
| `children` | Коллекция дочерних **элементов** |
| `firstElementChild` / `lastElementChild` | Первый / последний дочерний элемент |
| `nextElementSibling` / `previousElementSibling` | Сосед-элемент слева/справа |
| `childElementCount` | Сколько дочерних элементов |
| `closest('.selector')` | Ближайший предок (начиная с самого элемента), подходящий под CSS-селектор, или `null` |

```js
const btn = document.querySelector('.delete-btn');

btn.closest('li');                    // карточка-пункт списка — родной контейнер
btn.closest('.card').dataset.id;      // подъём до карточки, чтение data-id
btn.parentElement.children.length;    // сколько ещё соседей в списке

// Перебор элементов списка без querySelectorAll:
for (const li of list.children) console.log(li.textContent);
// или list.querySelectorAll('li') — тогда удобнее
```

`node.contains(other)` — узнать «я внутри него?»; `compareDocumentPosition` — точное взаимное расположение узлов.

## Таблица методов поиска (слайд занятия)

| Метод поиска             | Ищет по...         | Возвращает...      | Ищет внутри элемента? | Живая коллекция? |
| ------------------------ | ------------------ | ------------------ | --------------------- | ---------------- |
| `querySelector`          | Любой CSS-selector | Один объект        | Да                    | Нет              |
| `querySelectorAll`       | Любой CSS-selector | Коллекцию объектов | Да                    | Нет              |
| `getElementById`         | id                 | Один объект        | Нет                   | Да               |
| `getElementsByTagName`   | теги или `*`       | Коллекцию объектов | Да                    | Да               |
| `getElementsByClassName` | имя класса         | Коллекцию объектов | Да                    | Да               |
| `getElementsByName`      | name               | Коллекцию объектов | Нет                   | Да               |

### Разбор по строкам

**querySelector** — универсал: любой CSS-селектор (`'.card', '#main', 'ul > li.active', '[data-x]'`), возвращает **первый** подходящий элемент или `null`. Ищет внутри элемента (`card.querySelector('h2')` — ищет только внутри card).

**querySelectorAll** — тот же синтаксис, но возвращает **все** совпадения. Искать внутри элемента тоже умеет. Коллекция статическая (см. ниже).

**getElementById** — самый быстрый поиск по уникальному `id`, только `document.getElementById('id')`, без контекста («ищет внутри элемента? Нет»). Возвращает один объект.

**getElementsByTagName** — все элементы с данным тегом (`div`, `*` — все). Обычно вызывают от `document` или от конкретного элемента: `list.getElementsByTagName('li')`.

**getElementsByClassName** — все элементы с данным классом. Контекст работает.

**getElementsByName** — элементы с атрибутом `name` (формы: input, select, textarea, форма; для input с radio работает группировка). Контекста нет — только целый документ.

## Живая vs статическая коллекция — что значит колонка

- **Живые** (`getElementsBy*` → `HTMLCollection`): список «привязан» к документу. Добавили `<li>` — он сразу появился в коллекции; удалили — исчез. Индекс `[0]`, `[1]`, `.length`, но **нет `forEach`** (нужен `for`).
- **Статические** (`querySelectorAll` → `NodeList`): снимок на момент вызова. Добавили элемент — коллекция не изменится, нужно искать заново. Зато есть `forEach` и методы вроде `entries()`.

```js
// Стучаться по классам — живёт:
const items = document.getElementsByClassName('item');
items.length; // 3

// querySelectorAll — снимок:
const itemsQS = document.querySelectorAll('.item');
itemsQS.forEach(el => console.log(el.textContent)); // работает

// Живую HTMLCollection перебираем классикой:
for (let i = 0; i < items.length; i++) { ... }
// или Array.from(items).forEach(...)
```

## Работа с содержимым и атрибутами

```js
const card = document.querySelector('.card');

card.textContent;        // только текст, без тегов (быстро, безопасно)
card.innerText;          // текст как отрисован (учитывает стили, медленнее)
card.innerHTML;          // HTML-код внутри — опасен при вставке пользовательского ввода (XSS)

const input = document.querySelector('#email');
input.value;             // значение поля
input.checked;           // состояние чекбокса/радио

// Атрибуты
card.getAttribute('data-id');
card.setAttribute('data-id', '42');
card.removeAttribute('data-id');
card.dataset.id;         // то же через dataset (data-id → dataset.id)
```

## Изменение DOM

```js
// Создание и вставка
const el = document.createElement('div');   // создать узел-элемент
const text = document.createTextNode('Текст'); // текстовый узел (безопасно от XSS)
el.append(text);                            // добавить текст в элемент

document.body.append(el);            // в конец
card.prepend(el);                    // в начало
card.before(el); card.after(el);     // до / после
el.remove();                         // удалить

// Дублирование и сравнение узлов
const copy = el.cloneNode(true);     // true — глубоко, с детьми; false — только сам узел
el.isEqualNode(copy);                // true: одинаковая структура
el === copy;                         // false: это два разных узла (это разные объекты!)

// Перемещение: вставка существующего узла = его перенос (не копия)
otherParent.append(el);              // элемент УХОДИТ из старого родителя

// Пакетная вставка: DocumentFragment — контейнер без родителя
const frag = document.createDocumentFragment();
for (const item of items) {
  const li = document.createElement('li');
  li.textContent = item.name;        // textContent безопаснее innerHTML
  frag.append(li);                   // копим во фрагменте
}
list.append(frag);                    // один reflow вместо N

// «Старый» API (то же самое, но verbose)
parent.insertBefore(newNode, refChild);   // вставить перед refChild
parent.replaceChild(newNode, oldChild);   // заменить узел
parent.removeChild(child);                // удалить

// Вставка готового HTML
list.insertAdjacentHTML('beforeend', '<li>Новый пункт</li>');
// insertAdjacentHTML: 'beforebegin' | 'afterbegin' | 'beforeend' | 'afterend'

// Классы
el.classList.add('active');
el.classList.remove('hidden');
el.classList.toggle('open');         // переключатель
el.classList.contains('active');     // проверка

// Стили напрямую (обычно лучше через classList)
el.style.backgroundColor = '#eee';
```

## События и делегирование

```js
button.addEventListener('click', (event) => {
  event.preventDefault();          // отменить действие по умолчанию
  console.log(event.target);       // элемент, на котором сработало
});
```

**Делегирование** — не навешивать обработчик на каждую кнопку, а один на общий контейнер:

```js
list.addEventListener('click', (e) => {
  const btn = e.target.closest('.delete-btn'); // ближайший подходящий предок
  if (!btn) return;
  btn.closest('li').remove();      // удаляем пункт
});
```

## DevTools для DOM

- **Elements** — дерево страницы, правый клик: Copy → Copy selector / Copy JS path, Break on (подсветка изменений)
- **Console:** `$0` — текущий выбранный элемент, `$` и `$$` — быстрые querySelector/querySelectorAll
- **Breakpoints** на поддереве: Debugger → Break on → subtree modifications

## DOM и оптимизация (связь с курсом)

- `textContent`/`innerHTML` перезаписывают содержимое — частые перезаписи вызывают **reflow/repaint**, что бьёт по скорости и LCP ([Конспект — 7-8. Способы ускорения загрузки сайтов](%D0%9A%D0%BE%D0%BD%D1%81%D0%BF%D0%B5%D0%BA%D1%82%20%E2%80%94%207-8.%20%D0%A1%D0%BF%D0%BE%D1%81%D0%BE%D0%B1%D1%8B%20%D1%83%D1%81%D0%BA%D0%BE%D1%80%D0%B5%D0%BD%D0%B8%D1%8F%20%D0%B7%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B8%20%D1%81%D0%B0%D0%B9%D1%82%D0%BE%D0%B2.md))
- Кэшировать результаты `querySelector` в переменные, не искать элемент в цикле
- Вставлять большой блок — одной вставкой (`insertAdjacentHTML` или `DocumentFragment`), а не по узлу
- `querySelectorAll`-снимок после массовых вставок придётся пересоздать — планировать порядок операций
- Лишние узлы в DOM (тысячи `div` от SPA-библиотек) → тормозит рендеринг и интерактивность (TTI)

## Термины

| Термин | Определение |
|--------|-------------|
| DOM | Объектная модель документа: HTML как дерево объектов в JavaScript |
| Узел (node) | Элемент дерева: тег, текст, атрибут, комментарий |
| nodeType | Числовой тип узла: 1 — элемент, 3 — текст, 8 — комментарий, 11 — фрагмент |
| HTMLCollection | «Живая» коллекция от `getElementsBy*` |
| NodeList | Коллекция от `querySelectorAll` — статическая, есть `forEach` |
| Sibling | Узел на том же уровне вложенности («сосед») |
| DocumentFragment | Контейнер без родителя: копим вставки, в DOM добавляем один раз |
| cloneNode | Копирование узла (`true` — глубоко, с детьми; `false` — только узел) |
| isEqualNode | Сравнение структуры двух узлов (а не идентичности объектов) |
| Делегирование | Один обработчик на контейнер вместо обработчиков на каждый элемент |
| Reflow | Пересчёт геометрии страницы после изменения DOM |
| Dataset | Доступ к `data-*` атрибутам через `el.dataset` |

## Вопросы для повторения

- Что такое DOM? Из чего состоит дерево документа?
- Какие типы узлов бывают (nodeType)? Чем элемент отличается от текстового узла?
- Почему `firstChild` может вернуть не тот элемент, который ожидаешь?
- Перечисли свойства навигации: только элементы vs все узлы. Зачем `closest`?
- Все методы из таблицы поиска: что ищут, что возвращают, есть ли контекст?
- Чем живая коллекция отличается от статической? Примеры.
- Почему у `HTMLCollection` нет `forEach`, а у `NodeList` есть?
- Чем `textContent` отличается от `innerText` и `innerHTML`?
- Зачем делегирование событий и как работает `closest`?
- Что делает `cloneNode(true)`? Чем `isEqualNode` отличается от `===`?
- Что произойдёт с узлом, если вставить его в другого родителя?
- Зачем DocumentFragment и какую проблему он решает?
- Какие приёмы работы с DOM влияют на скорость страницы?

## 📎 Связанные

- Практическая работа №1 — Пользовательские запросы (Рыбаков) — DevTools, HTTP/REST в этом курсе
- [Конспект — 9. Шаблоны проекта](%D0%9A%D0%BE%D0%BD%D1%81%D0%BF%D0%B5%D0%BA%D1%82%20%E2%80%94%209.%20%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD%D1%8B%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0.md) — шаблоны и вёрстка проекта
- [Конспект — 7-8. Способы ускорения загрузки сайтов](%D0%9A%D0%BE%D0%BD%D1%81%D0%BF%D0%B5%D0%BA%D1%82%20%E2%80%94%207-8.%20%D0%A1%D0%BF%D0%BE%D1%81%D0%BE%D0%B1%D1%8B%20%D1%83%D1%81%D0%BA%D0%BE%D1%80%D0%B5%D0%BD%D0%B8%D1%8F%20%D0%B7%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B8%20%D1%81%D0%B0%D0%B9%D1%82%D0%BE%D0%B2.md) — reflow/repaint и LCP
- Предмет: Оптимизация веб-приложений · 🎓 MOC — Учёба
