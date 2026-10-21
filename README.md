# Sonoma Glass для Omarchy

Тема в стиле macOS: Liquid Glass с преломлением по краям, прозрачный Foot, стеклянные кнопки с локальными волнами, компактные отступы, меню с вычислениями и конвертациями, иконки приложений и папок, блокировка, опциональные экраны входа и загрузки. В комплекте только шесть выбранных обоев Macintosh, без видео и дополнительных коллекций.

## Установка

Нужны Omarchy с Hyprland **0.56.x**, Python **3.11+**, Quickshell, `git`, `base-devel`, `pkgconf`, `wayland-protocols`, `qt6-shadertools`, заголовки установленного Hyprland. Для установки иконок нужен `gtk-update-icon-cache` (пакет `gtk4`). `gum` делает CLI удобнее; без него есть текстовое меню. ImageMagick нужен только для изменения цвета яблока на экране загрузки.

Через штатную установку тем Omarchy:

```bash
omarchy theme install https://github.com/Rulunchic/sonoma-glass.git
bash ~/.config/omarchy/themes/sonoma-glass/install.sh
```

Либо из собственного клона:

```bash
git clone https://github.com/Rulunchic/sonoma-glass.git
cd sonoma-glass
./install.sh
```

Установщик открывает интерактивное меню. В разделе **Компоненты** можно включить и выключить части темы, в остальных разделах — настроить внешний вид. Завершение: **Сохранить и выйти**. До этого решения установка не меняет рабочий стол.

Без интерактивных вопросов:

```bash
./install.sh --yes
./install.sh --yes --no-icons --no-bubbles --no-lock
./install.sh --yes --set terminal.alpha=0.65 --set glass.terminal.refraction_strength=1.8
./install.sh --yes --config ~/sonoma-settings.json
```

Также доступны `--no-glass`, `--no-windows`, `--no-layers`, `--no-terminal`, `--no-buttons`, `--no-menu`, `--with-login`, `--with-boot`, `--rebuild`, `--refresh-icons`. Настройки существующей установки сохраняются при обновлении. Отключение терминального стекла оставляет обычное размытие и выбранную прозрачность фона.

HyprGlass собирается локально по зафиксированной версии с патчем из `patches/hyprglass-liquidjs.patch`. Готовые бинарники под чужую версию Hyprland не распространяются. Установщик сохраняет предыдущие конфиги в `~/.local/share/sonoma-glass/backups/`. Системные пакеты автоматически не устанавливаются.

Omarchy фильтрует исполняемые конфиги скачанных тем; второй шаг устанавливает проверяемые локальные файлы. При запуске из папки тем отдельный git-клон сохраняется в `~/.local/share/sonoma-glass/source`, а тема становится локальной и появляется в обычном списке тем.

## Настройки в верхней панели

Значок **Sonoma Glass** появляется справа в баре, рядом с системным треем. На вкладке **Основное** — четыре пресета, выбор области и несколько главных ползунков. **Все параметры** содержит поиск по полному каталогу и выбор раздела. **Профили** — сохранение своих вариантов, загрузку, импорт и экспорт. Ползунки имеют область захвата высотой 32 px: число меняется плавно при движении, настройки применяются после отпускания мыши. На основном экране прозрачность задаётся в процентах; больше процентов — прозрачнее фон. Выбор цвета встроен в панель: поле насыщенности и яркости, спектр оттенков, альфа, готовые цвета и HEX, без системных диалогов.

- Пять отдельных профилей материала: окна, терминал, бар, меню, виджеты.
- Две модели: Liquid Glass JS и стандартная модель HyprGlass.
- Преломление, ширина края терминала, размытие, линза, зерно, блики, Френель, аберрация, окрашивание, яркость, контраст и насыщенность.
- Плотность окон и фона терминала, прозрачность панели, меню, виджетов, уведомлений и кнопок.
- Цвета, рамки, отступы, размеры интерфейса и шрифт терминала.
- Волны внутри кнопок: сила, длительность, упругость, затухание, поведение при наведении и движении. Глобального эффекта вокруг мышки нет.
- Частота обновления фона, кэширование и маски поверхностей — на вкладке **Все параметры**.
- Пресеты **Сбалансированный**, **Прозрачный**, **Матовое стекло**, **Спокойный**; пользовательские профили, импорт/экспорт и откат.

CLI и виджет используют один проверяемый каталог параметров и файл `~/.config/omarchy/sonoma-glass/settings.json`. Изменения виджета применяются автоматически; ползунки сохраняют значение после отпускания мыши. Фоновые обновления сохраняют положение захваченного бегунка. Настройки входа и загрузки находятся в разделах **Компоненты** и **Блокировка, вход и загрузка** на вкладке **Все параметры**. Некорректные значения отклоняются; при ошибке конфигурации Hyprland возвращается предыдущий вариант. Foot применяет новый шрифт и фон **в новых окнах**.

## CLI

```bash
sonoma-glass configure
sonoma-glass list
sonoma-glass get terminal.alpha
sonoma-glass set terminal.alpha 0.66
sonoma-glass set glass.terminal.refraction_strength 2.0
sonoma-glass set terminal.rim_width 36
sonoma-glass set shell.popups.background-alpha 0.35
sonoma-glass set desktop.active_border '#82c5ff'
sonoma-glass set components.bubbles false
sonoma-glass preset frosted
sonoma-glass profile save 'Моё стекло'
sonoma-glass profile load 'Моё стекло'
sonoma-glass export ~/sonoma-settings.json
sonoma-glass import ~/sonoma-settings.json
sonoma-glass undo
sonoma-glass status
```

`sonoma-glass set-json '{"terminal.alpha":0.7,"glass.terminal.blur_strength":1.2}'` применяет несколько параметров одной операцией. `--no-apply` у `set`/`set-json` сохраняет значения для последующего `sonoma-glass apply`. `schema` выводит полный каталог с типами и диапазонами.

Цвета — `#RRGGBB`; цвета материала и рамок окон также принимают `#RRGGBBAA`. У остальных поверхностей есть отдельные параметры непрозрачности. Чем ближе непрозрачность к 1, тем плотнее фон. Значение 0 полностью прозрачно. Стеклянный материал не делает непрозрачное содержимое приложения прозрачным: для видимого фона под ним нужна прозрачность окна или приложения.

## Обои

В штатном выборе обоев доступны только `Blue_icons`, `Blue_Computer`, `Logo_Blue`, `Purple_icons`, `Grey_Icons`, `File_Yellow`. При установке выбирается `Blue_icons.jpg` либо сохранённое значение `desktop.wallpaper`. Обои входа настраиваются отдельно — `system.wallpaper`.

```bash
sonoma-glass wallpaper
sonoma-glass wallpaper Blue_Computer.jpg
```

## Вход и загрузка

По умолчанию новая установка не включает экраны входа и загрузки; существующая настройка этой темы сохраняется. В виджете включите нужные компоненты и нажмите **Применить системные**. Появится штатный запрос пароля администратора.

```bash
sonoma-glass set components.login true
sonoma-glass set components.boot true
sonoma-glass system-apply
```

Либо установите с `--with-login --with-boot`. В терминале используется `sudo`, из виджета — `pkexec`. Обычная настройка стекла прав администратора не требует.

Вход использует SDDM и штатную проверку пароля, блокировка — штатный PAM/WlSessionLock Omarchy. Оформление загрузки использует Plymouth и существующую сборку загрузочных образов. Пароли не сохраняются. SDDM и сессия не перезапускаются; перезагрузка автоматически не выполняется. Изменения входа/загрузки видны при следующем запуске. Системные селекторы сохраняются в `/var/lib/sonoma-glass-settings`; отключение компонентов возвращает исходный выбор темы. Автовход отдельно задаётся `system.autologin` и применяется системной кнопкой.

## Обновление

Запустите `./update.sh` из исходного git-клона. При установке через Omarchy:

```bash
~/.local/share/sonoma-glass/source/update.sh
```

После совместимого обновления Hyprland: `sonoma-glass install --yes --rebuild`. Иконки обновляются с `--refresh-icons`. Установка с другим Hyprland требует совместимого исходного HyprGlass.

## Отключение

Виджет и CLI позволяют выключить отдельные компоненты. Чтобы вернуться к штатному меню и блокировке:

```bash
sonoma-glass set components.menu false
sonoma-glass set components.lock false
sonoma-glass set components.buttons false
sonoma-glass set components.bubbles false
omarchy plugin disable sonoma.settings
omarchy theme set <другая-тема>
```

Перед удалением пользовательских файлов выключите вход и загрузку и выполните `sonoma-glass system-apply`. Для удаления иконок и восстановления изменённых desktop-файлов используйте `python3 ./uninstall-icons.py` из исходного клона.

## Авторы и лицензии

Шесть обоев — [Basic Apple Guy](https://basicappleguy.com/haberdashery/macintoshwallpapers); включены по просьбе владельца репозитория. Используйте как личные обои рабочего стола и учитывайте условия автора. Проект не связан с Apple или Basic Apple Guy.

Иконки приложений, папок, устройств и файлов — [WhiteSur](https://github.com/vinceliuice/WhiteSur-icon-theme), ревизия `73d8040`, GPL-3.0. Включённый знак загрузки взят из этого набора; лицензия — `WHITESUR-ICONS-LICENSE`. Дополнительные иконки [Nuno Coelho Santos](https://github.com/nunosans/big-sur-icons) скачиваются при установке и распространяются по CC BY-NC 4.0. Приложения с названиями, заканчивающимися на craft, сохраняют свои исходные иконки.

Код темы/установщика — MIT (`LICENSE`). Адаптированные элементы Omarchy — MIT (`OMARCHY-LICENSE`). HyprGlass — BSD-3-Clause (`HYPRGLASS-LICENSE`). Формулы модели Liquid Glass JS адаптированы из [dashersw/liquid-glass-js](https://github.com/dashersw/liquid-glass-js), MIT (`LIQUID-GLASS-JS-LICENSE`). Шрифты Apple не включены; можно выбрать установленный SF Mono или другой шрифт.
