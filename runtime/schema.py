"""One settings catalogue shared by the installer, CLI and bar widget."""
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parent
GROUPS = []
OPTIONS = []


def group(key, label):
    GROUPS.append({'id': key, 'label': label})


def option(key, label, default, kind='number', minimum=0, maximum=1, step=.01,
           hint='', advanced=False, choices=None, category=None):
    item = dict(key=key, label=label, default=default, type=kind,
                group=category or GROUPS[-1]['id'], hint=hint, advanced=advanced)
    if kind in ('number', 'integer'):
        item.update(min=minimum, max=maximum, step=step)
    if kind == 'color':
        item['alpha'] = key.startswith('glass.') or key in ('desktop.active_border','desktop.inactive_border','desktop.shadow_color')
    if choices:
        item['choices'] = choices
    OPTIONS.append(item)


group('components', 'Компоненты')
for key, title, default, hint in [
    ('glass', 'Liquid Glass', True, 'Общий переключатель преломления'),
    ('windows', 'Стекло в окнах', True, ''),
    ('layers', 'Стекло в панели и виджетах', True, ''),
    ('terminal', 'Стекло в терминале', True, ''),
    ('buttons', 'Стеклянные кнопки', True, ''),
    ('bubbles', '«Буль-буль» внутри кнопок', True, 'Без эффекта вокруг курсора'),
    ('menu', 'Меню Sonoma с вычислениями', True, ''),
    ('icons', 'Иконки Sonoma Glass', True, 'Использовать установленный набор; установка через CLI'),
    ('lock', 'Экран блокировки macOS', True, 'Штатная проверка пароля Omarchy'),
    ('login', 'Экран входа macOS', False, 'Применяется системной кнопкой ниже'),
    ('boot', 'Загрузка с яблоком', False, 'Требует системного применения и пересборки загрузочного образа'),
]:
    option('components.'+key, title, default, 'boolean', hint=hint)

group('desktop', 'Окна и отступы')
option('desktop.wallpaper', 'Обои рабочего стола', 'Blue_icons.jpg', 'choice', choices=[
 'Blue_icons.jpg','Blue_Computer.jpg','Logo_Blue.jpg','Purple_icons.jpg','Grey_Icons.jpg','File_Yellow.jpg'])
for key, label, default, lo, hi, step in [
    ('active_opacity', 'Непрозрачность активного окна', .90, .25, 1, .01),
    ('inactive_opacity', 'Непрозрачность неактивного окна', .84, .25, 1, .01),
    ('gaps_in', 'Расстояние между окнами', 4, 0, 40, 1),
    ('gaps_out', 'Отступ от краёв экрана', 7, 0, 60, 1),
    ('rounding', 'Скругление окон', 16, 0, 60, 1),
    ('rounding_power', 'Форма скругления', 2.0, 2, 6, .1),
    ('border_size', 'Толщина рамки', 2, 0, 8, 1),
    ('shadow_range', 'Размер тени', 24, 0, 80, 1),
]:
    option('desktop.'+key, label, default, 'integer' if step == 1 else 'number', lo, hi, step)
option('desktop.shadows', 'Видимые тени окон', False, 'boolean')
option('desktop.active_border', 'Рамка активного окна', '#64b5ff', 'color')
option('desktop.inactive_border', 'Рамка неактивного окна', '#ffffff24', 'color')
option('desktop.shadow_color', 'Цвет тени', '#00000055', 'color')

group('terminal', 'Терминал')
option('terminal.alpha', 'Непрозрачность фона', .74, hint='Foot применяет фон и шрифт в новых окнах')
option('terminal.font', 'Шрифт', 'JetBrainsMono Nerd Font', 'text', hint='Имя установленного шрифта; например SF Mono')
option('terminal.font_size', 'Размер шрифта', 9, minimum=6, maximum=28, step=.5)
option('terminal.rim_width', 'Ширина преломления по краям', 28, minimum=4, maximum=96, step=1,
       hint='Для модели Liquid Glass; центр окна остаётся ровным')
option('terminal.foreground', 'Цвет текста', '#f5f5f7', 'color')
option('terminal.background', 'Цвет фона', '#1c1c1e', 'color')

FIELDS = [
    ('refraction_strength', 'Сила преломления', 1., 0, 6, .05, False),
    ('blur_strength', 'Сила размытия', .85, 0, 4, .05, False),
    ('blur_iterations', 'Проходы размытия', 2, 1, 8, 1, False),
    ('glass_opacity', 'Плотность стекла', 1., 0, 1, .01, False),
    ('brightness', 'Яркость', 1., .2, 2, .02, False),
    ('contrast', 'Контраст', 1., 0, 2.5, .02, False),
    ('saturation', 'Насыщенность', 1., 0, 2.5, .02, False),
    ('chromatic_aberration', 'Хроматическая аберрация', 0., 0, 3, .02, False),
    ('fresnel_strength', 'Светящийся край (Френель)', .12, 0, 4, .02, False),
    ('specular_strength', 'Сила блика', .35, 0, 4, .02, False),
    ('bevel_strength', 'Яркость окантовки', .28, 0, 1, .01, False),
    ('bevel_size', 'Ширина окантовки', 3., 0, 16, .25, False),
    ('bevel_shadow', 'Затемнение окантовки', 0., 0, 1, .01, False),
    ('lens_distortion', 'Линза в центре', 0., 0, 3, .05, False),
    ('noise_strength', 'Зерно', 0., 0, 1, .01, True),
    ('edge_thickness', 'Ширина зоны блика', .024, .001, .15, .001, True),
    ('refraction_flow', 'Направление вдоль края', 1., 0, 1, .02, True),
    ('refraction_spread', 'Распределение преломления', 1., 0, 1, .02, True),
    ('specular_angle', 'Угол блика', 0., 0, 360, 1, True),
    ('bevel_angle', 'Угол света окантовки', 315., 0, 360, 1, True),
    ('fresnel_tint', 'Окрашивание края', 0., 0, 1, .01, True),
    ('bevel_tint', 'Окрашивание окантовки', 0., 0, 1, .01, True),
    ('vibrancy', 'Живость цвета', 0., 0, 2, .02, True),
    ('vibrancy_darkness', 'Живость в тенях', 0., 0, 1, .01, True),
    ('adaptive_dim', 'Адаптивное затемнение', 0., 0, 1, .01, True),
    ('adaptive_boost', 'Адаптивное осветление', 0., 0, 1, .01, True),
    ('self_sample', 'Примесь содержимого окна', 0., 0, 1, .01, True),
]
group('glass.common', 'Стекло · качество')
option('glass.common.skip_opaque', 'Пропускать полностью непрозрачные окна', False, 'boolean', advanced=True)
option('glass.common.blur_fold', 'Совмещать проход размытия', True, 'boolean', advanced=True)
option('glass.common.background_cache', 'Кэшировать фон окон', True, 'boolean', advanced=True)
option('glass.common.windows_live', 'Обновлять фон под окнами', True, 'boolean', advanced=True)
option('glass.common.windows_fps', 'Частота обновления фона окон', 30, 'integer', 1, 144, 1, advanced=True)
option('glass.common.layers_live', 'Обновлять фон под виджетами', True, 'boolean', advanced=True)
option('glass.common.layers_fps', 'Частота обновления фона виджетов', 30, 'integer', 1, 144, 1, advanced=True)
option('glass.common.force_live', 'Постоянно обновлять фон виджетов', False, 'boolean', advanced=True,
       hint='Повышает нагрузку на GPU, даже если фон неподвижен')
SCOPES = ['windows', 'terminal', 'bar', 'menu', 'widgets']
for scope, title in zip(SCOPES, ['Стекло · окна', 'Стекло · терминал', 'Стекло · бар', 'Стекло · меню', 'Стекло · виджеты']):
    group('glass.'+scope, title)
    option(f'glass.{scope}.model', 'Модель стекла', 'liquidjs', 'choice',
           choices=['liquidjs', 'native'], hint='Liquid Glass JS или стандартная модель HyprGlass')
    for key, label, default, lo, hi, step, advanced in FIELDS:
        if scope == 'terminal' and key == 'refraction_strength': default = 1.6
        if scope == 'terminal' and key == 'blur_strength': default = .65
        hint = 'Для стандартной модели HyprGlass' if key in ['refraction_flow', 'refraction_spread'] else ''
        option(f'glass.{scope}.{key}', label, default,
               'integer' if key == 'blur_iterations' else 'number', lo, hi, step,
               advanced=advanced, hint=hint)
    for key, label in [('tint_color','Цвет стекла и его альфа'), ('fresnel_color','Цвет светящегося края'), ('bevel_color','Цвет окантовки')]:
        option(f'glass.{scope}.{key}', label, '#ffffff00', 'color', advanced=True,
               hint='Прозрачность 00 оставляет исходный цвет; ff — полное окрашивание')
    option(f'glass.{scope}.xray', 'Фон рабочего стола сквозь другие окна', False, 'boolean', advanced=True)
    if scope in ('bar','menu','widgets'):
        option(f'glass.{scope}.enabled', 'Преломление в этой области', True, 'boolean')
        option(f'glass.{scope}.mask_threshold', 'Порог маски стекла', .32 if scope=='menu' else .12,
               advanced=True, hint='Позволяет отсечь края прокрутки и полупрозрачные тени')
        option(f'glass.{scope}.mask_feather', 'Мягкость маски', .12 if scope=='menu' else .25, advanced=True)
        mask_mode_default = 'alpha' if scope == 'bar' else 'auto'
        mask_mode_hint = 'Альфа-канал полупрозрачного фона панели задаёт область стекла.' if scope == 'bar' else ''
        option(f'glass.{scope}.mask_mode', 'Источник формы стекла', mask_mode_default, 'choice',
               hint=mask_mode_hint,
               choices=['auto','alpha','region'], advanced=True)

group('bubbles', 'Кнопки и «буль-буль»')
for key, label, default, lo, hi, step in [
    ('strength', 'Сила деформации', 1., 0, 2, .05),
    ('wave_strength', 'Яркость волны', 1., 0, 2, .05),
    ('hover_strength', 'Волна при наведении', .55, 0, 1, .05),
    ('move_strength', 'Волна при движении', .38, 0, 1, .05),
    ('duration', 'Длительность волны, мс', 620, 160, 1600, 10),
    ('spring', 'Упругость', 4.2, .5, 5, .1),
    ('damping', 'Затухание', .24, .1, 1, .02),
    ('light_follow', 'Сглаживание блика, мс', 65, 0, 250, 5),
    ('move_interval', 'Интервал волн движения, мс', 180, 100, 600, 10),
]:
    option('bubbles.'+key,label,default,minimum=lo,maximum=hi,step=step)
option('bubbles.motion', 'Реакция на движение внутри кнопки', True, 'boolean')

group('blur', 'Обычное размытие')
option('blur.enabled','Размытие Hyprland',True,'boolean')
for key,label,default,lo,hi,step in [('size','Размер',30,1,64,1),('passes','Проходы',4,1,6,1),
    ('noise','Зерно',.012,0,.2,.001),('contrast','Контраст',1.08,.2,2,.02),
    ('brightness','Яркость',1.06,.2,2,.02),('vibrancy','Насыщенность',.32,0,1,.01)]:
    option('blur.'+key,label,default,'integer' if key in ['size','passes'] else 'number',lo,hi,step)
option('blur.popups','Размывать всплывающие поверхности',True,'boolean')
option('blur.xray','Размывать только обои',False,'boolean')
option('blur.ignore_opacity','Не ослаблять размытие прозрачностью',True,'boolean',advanced=True)

group('palette','Основная палитра')
for key,value in tomllib.loads((ROOT/'templates/colors.toml').read_text()).items():
    if isinstance(value,str) and value.startswith('#'):
        option('palette.'+key,key.replace('_',' '),value,'color')

SECTION_LABELS={'bar':'Панель сверху','controls':'Цвета кнопок','popups':'Виджеты',
 'menu':'Меню','launcher':'Поиск приложений','notifications':'Уведомления',
 'tooltip':'Подсказки','lock':'Цвета блокировки','polkit':'Системные запросы',
 'spacing':'Размеры интерфейса','font':'Шрифт интерфейса','hyprland':'Рамки интерфейса'}
for section,values in tomllib.loads((ROOT/'templates/shell.toml').read_text()).items():
    if not isinstance(values,dict): continue
    group('shell.'+section,SECTION_LABELS.get(section,section))
    for key,value in values.items():
        label=key.replace('-',' ')
        kind='boolean' if isinstance(value,bool) else 'color' if isinstance(value,str) and value.startswith('#') else 'text' if isinstance(value,str) else 'number'
        alpha='alpha' in key
        lo,hi,step=(0,1,.01) if alpha else (0,100,1)
        if section=='spacing' and key=='scale': lo,hi,step=.65,1.6,.05
        if section=='font' and key=='base-size': lo,hi,step=8,28,1
        if section=='bar' and key.startswith('size-'): lo,hi,step=20,64,1
        option(f'shell.{section}.{key}',label,value,kind,lo,hi,step,
               hint='Непрозрачность: 0 — прозрачный, 1 — непрозрачный' if alpha else '')

group('system','Блокировка, вход и загрузка')
option('system.autologin','Автоматический вход без пароля',False,'boolean',hint='Только после системного применения')
option('system.wallpaper','Обои экрана входа','Blue_icons.jpg','choice',choices=[
 'Blue_icons.jpg','Blue_Computer.jpg','Logo_Blue.jpg','Purple_icons.jpg','Grey_Icons.jpg','File_Yellow.jpg'])
option('system.boot_background','Цвет фона загрузки','#000000','color')
option('system.boot_foreground','Цвет яблока и полосы','#ffffff','color')
option('system.lock_blur','Размытие обоев блокировки',.25)
option('system.clock_size','Размер часов',144,minimum=64,maximum=180,step=1)

INDEX = {item['key']:item for item in OPTIONS}
DEFAULTS = {key:item['default'] for key,item in INDEX.items()}
DOCUMENT = {'version':1,'groups':GROUPS,'options':OPTIONS}
