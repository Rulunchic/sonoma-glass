"""Install user-owned theme assets; privileged startup appearance is separate."""
import datetime
import hashlib
import json
import os
import pwd
from pathlib import Path
import re
import shutil
import subprocess

import settings as store
from schema import DEFAULTS


def run(args, **kwargs):
    subprocess.run([str(a) for a in args],check=True,**kwargs)


def copy_tree(source, target):
    shutil.copytree(source,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))


def install_icons(source, refresh=False):
    for script in ['install-whitesur-icons.py','install-bigsur-icons.py','install-app-icon-aliases.py']:
        command=['python3',source/script]
        if refresh and script=='install-bigsur-icons.py': command+=['--force']
        run(command)


def compile_shader(directory):
    qsb=shutil.which('qsb') or '/usr/lib/qt6/bin/qsb'
    if not Path(qsb).exists(): raise RuntimeError('Нужен qt6-shadertools (qsb) для шейдеров кнопок')
    run([qsb,'--qt6','-o',directory/'liquid-control.frag.qsb',directory/'liquid-control.frag'])


def build_plugin(source, rebuild=False):
    if not shutil.which('hyprctl'): raise RuntimeError('Нужен Hyprland 0.56 с development-файлами')
    version=subprocess.check_output(['hyprctl','version'],text=True)
    if not re.search(r'Hyprland 0\.56\.',version): raise RuntimeError('Этот HyprGlass рассчитан на Hyprland 0.56')
    patch=source/'patches/hyprglass-liquidjs.patch'
    fingerprint=hashlib.sha256(patch.read_bytes()+version.encode()).hexdigest()
    marker=store.SUPPORT/'plugins/build.json'
    if store.PLUGIN.exists() and marker.exists() and json.loads(marker.read_text()).get('fingerprint')==fingerprint and not rebuild:
        return
    for command in ['git','make','c++','pkg-config','wayland-scanner']:
        if not shutil.which(command): raise RuntimeError('Не найдена зависимость: '+command)
    run(['pkg-config','--exists','hyprland','pixman-1','libdrm','wayland-server'])
    # A dedicated worktree: never reset a user's existing source checkout.
    checkout=store.SUPPORT/'deps'/('liquidjs-'+fingerprint[:12])
    commit=(source/'HYPRGLASS-COMMIT').read_text().strip()
    if not (checkout/'.git').exists():
        checkout.parent.mkdir(parents=True,exist_ok=True)
        run(['git','clone','--no-checkout','https://github.com/hyprnux/hyprglass.git',checkout])
        run(['git','-C',checkout,'checkout','--detach',commit])
    applied=checkout/'.sonoma-patch'
    if not applied.exists():
        run(['git','-C',checkout,'apply','--check',patch])
        run(['git','-C',checkout,'apply',patch])
        applied.write_text(fingerprint)
    run(['make','clean'],cwd=checkout)
    run(['make','-j'+str(min(os.cpu_count() or 2,4)),'HYPRGLASS_VERSION=0.10.0-liquidjs.5'],cwd=checkout)
    store.PLUGIN.parent.mkdir(parents=True,exist_ok=True)
    temporary=store.PLUGIN.with_suffix('.so.new')
    shutil.copyfile(checkout/'hyprglass.so',temporary)
    # A mapped shared object must never be modified in place.
    os.replace(temporary,store.PLUGIN)
    store.atomic(marker,store.json_text({'fingerprint':fingerprint,'hyprland':version.strip()}))


def clone(name):
    user=os.environ.get('USER',store.HOME.name)
    target=store.HOME/'.config/omarchy/plugins'/(user+'.'+name)
    if not (target/'manifest.json').exists(): run(['omarchy','plugin','clone','omarchy.'+name])
    return target


def install_widgets(source):
    glass=store.HOME/'.config/omarchy/glass'
    copy_tree(source/'runtime/glass',glass)
    compile_shader(glass)
    # Clone first, so official IPC scope and authentication stay intact.
    for name in ['audio','monitor','network','bluetooth','power']:
        target=clone(name)
        for file in target.glob('*.qml'):
            text=file.read_text()
            original=text
            replacements={'Button':'LiquidButton','CursorSurface':'LiquidCursorSurface','ToggleSwitch':'LiquidSwitch',
                'PanelSlider':'LiquidSlider','ActionButton':'LiquidActionButton','BarIconButton':'LiquidBarIconButton'}
            for old,new in replacements.items():
                text=re.sub(r'\b'+old+r'\s*\{',new+' {',text)
                text=re.sub(r'(?<![\w.])'+new+r'\s*\{','Glass.'+new+' {',text)
            text=re.sub(r'(?<![\w.])KeyboardPanel\s*\{','Glass.LiquidPanel {',text)
            if text!=original and 'import "../../glass" as Glass' not in text:
                text='import "../../glass" as Glass\n'+text
            if text!=original: store.atomic(file,text)
    menu=clone('menu')
    for file in (source/'runtime/menu').iterdir():
        if file.is_file(): shutil.copy2(file,menu/file.name)
    lock=clone('lock')
    shutil.copy2(source/'runtime/lock/LockView.qml',lock/'LockView.qml')
    query=store.HOME/'.local/bin/omarchy-menu-live-query'
    query.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source/'runtime/menu-live-query.py',query)
    query.chmod(0o755)
    copy_tree(source/'plugins/sonoma.settings',store.HOME/'.config/omarchy/plugins/sonoma.settings')
    path=store.HOME/'.config/omarchy/shell.json'
    doc=json.loads(path.read_text())
    right=doc.setdefault('bar',{}).setdefault('layout',{}).setdefault('right',[])
    if not any(row.get('id')=='sonoma.settings' for row in right):
        right.insert(1 if right and right[0].get('id')=='omarchy.tray' else 0,{'id':'sonoma.settings'})
    doc['disabledPlugins']=[name for name in doc.get('disabledPlugins',[]) if name!='sonoma.settings']
    store.atomic(path,store.json_text(doc))


def prepare_system(s):
    stage=store.SUPPORT/'system-stage'
    copy_tree(store.ROOT/'login',stage)
    username=pwd.getpwuid(os.getuid()).pw_name
    store.atomic(stage/'request.json',store.json_text({'user':username,'login':s['components.login'],
        'boot':s['components.boot'],'autologin':s['system.autologin']}))
    wallpaper=store.THEME/'backgrounds'/s['system.wallpaper']
    shutil.copy2(wallpaper,stage/'sddm/background.jpg')
    main=(stage/'sddm/Main.qml').read_text().replace('"__SONOMA_USER__"',json.dumps(username))
    main=main.replace('blur: 0.25','blur: '+str(s['system.lock_blur']))
    main=main.replace('Math.min(144, root.height * 0.16)',f"Math.min({s['system.clock_size']}, root.height * 0.20)")
    store.atomic(stage/'sddm/Main.qml',main)
    # Standalone SDDM has QtQuick but no Quickshell/qs.Commons imports.
    chrome=(store.ROOT/'glass/LiquidChrome.qml').read_text().replace('import qs.Commons\n','')
    chrome=chrome.replace('Style.cornerRadius','16').replace('Color.accent',json.dumps(s['palette.accent']))
    def replace_value(match): return json.dumps(s.get(match.group(1),json.loads(match.group(2))))
    chrome=re.sub(r'GlassSettings\.value\("([^"]+)",\s*([^\)]+)\)',replace_value,chrome)
    store.atomic(stage/'sddm/LiquidChrome.qml',chrome)
    compile_shader(stage/'sddm')
    rgb=[int(s['system.boot_background'][i:i+2],16)/255 for i in (1,3,5)]
    script=(stage/'plymouth/sonoma-glass.script').read_text()
    for suffix in ['Top','Bottom']:
        script=re.sub(r'Window\.SetBackground'+suffix+r'Color\([^;]+;',f'Window.SetBackground{suffix}Color('+', '.join(map(str,rgb))+');',script)
    store.atomic(stage/'plymouth/sonoma-glass.script',script)
    color=s['system.boot_foreground'][:7]
    if color!='#ffffff':
        if not shutil.which('magick'): raise RuntimeError('Для окраски загрузки нужен ImageMagick')
        for name in ['logo.png','progress_bar.png','bullet.png','lock.png']:
            run(['magick',stage/'plymouth'/name,'-fill',color,'-colorize','100',stage/'plymouth'/name])
    return stage


def install(a):
    if os.geteuid()==0: raise ValueError('Запускайте install.sh от обычного пользователя, без sudo')
    if not shutil.which('qsb') and not Path('/usr/lib/qt6/bin/qsb').exists():
        raise ValueError('Для установки нужен пакет qt6-shadertools')
    source=a.source.expanduser().resolve()
    if not (source/'runtime/schema.py').exists(): raise ValueError('Не найден исходный каталог темы: '+str(source))
    first=not store.FILE.exists()
    changes={}
    if first:
        if (store.HOME/'.local/share/fonts/apple-sf-mono').exists(): changes['terminal.font']='SF Mono'
        selector=Path('/etc/sddm.conf.d/zz-sonoma-glass.conf')
        if selector.exists() and 'Current=sonoma-glass' in selector.read_text(): changes['components.login']=True
        ply=Path('/etc/plymouth/plymouthd.conf')
        if ply.exists() and 'Theme=sonoma-glass' in ply.read_text(): changes['components.boot']=True
    if a.config:
        doc=json.loads(a.config.expanduser().read_text()); changes.update(doc.get('values',doc))
    for name in ['glass','windows','layers','terminal','icons','menu','lock','buttons','bubbles']:
        if getattr(a,'no_'+name): changes['components.'+name]=False
    if a.with_login: changes['components.login']=True
    if a.with_boot: changes['components.boot']=True
    for assignment in a.set:
        if '=' not in assignment: raise ValueError('--set требует KEY=VALUE')
        key,value=assignment.split('=',1); changes[key]=store.parse(key,value)
    store.validate(changes)
    # All choices are made before touching the installed desktop.
    if not a.yes:
        from cli import configure
        if not os.isatty(0): raise ValueError('Используйте --yes для установки без терминала')
        result=configure(staged=True,initial={**store.load(),**changes})
        if result is None: print('Установка отменена.'); return
        changes.update(result)
    print('Sonoma Glass: подготовка установки…',flush=True)
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup=store.SUPPORT/'backups'/stamp
    backup.mkdir(parents=True,exist_ok=True)
    for path in [store.FILE,store.HOME/'.config/omarchy/shell.json',store.HOME/'.config/foot/foot.ini']:
        if path.exists():
            target=backup/path.relative_to(store.HOME)
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,target)
    build_plugin(source,a.rebuild)
    # Keep the source checkout separate from icon backup state and runtime.
    destination=store.SUPPORT/'runtime'
    if (source/'runtime').resolve()!=destination.resolve(): copy_tree(source/'runtime',destination)
    store.atomic(store.SUPPORT/'installation.json',store.json_text({'source':str(source),'version':1}))
    binpath=store.HOME/'.local/bin/sonoma-glass'
    if binpath.exists() and 'sonoma-glass-test' in binpath.read_text(): shutil.copy2(binpath,backup/'sonoma-glass-legacy')
    store.atomic(binpath,'#!/usr/bin/env bash\nexec python3 "$HOME/.local/share/sonoma-glass/runtime/cli.py" "$@"\n')
    binpath.chmod(0o755)
    values={**store.load(),**changes}
    if values['components.icons'] and (a.refresh_icons or not (store.HOME/'.local/share/icons/SonomaGlass-dark/index.theme').exists()):
        install_icons(source,a.refresh_icons)
    store.THEME.mkdir(parents=True,exist_ok=True)
    copy_tree(source/'backgrounds',store.THEME/'backgrounds')
    allowed={p.name for p in (source/'backgrounds').iterdir() if p.is_file()}
    for file in (store.THEME/'backgrounds').iterdir():
        if file.is_file() and file.name not in allowed: file.unlink()
    store.commit(changes)
    # Readers see complete settings/schema on their very first load.
    install_widgets(source)
    store.sync_components(store.load())
    baseline=store.profile_path('Исходная настройка')
    if not baseline.exists(): store.atomic(baseline,store.json_text({'version':1,'values':store.load()}))
    # A local theme folder is needed for Omarchy to allow its Lua config.
    if (store.THEME/'.git').exists():
        shutil.move(str(store.THEME/'.git'),str(backup/'theme.git'))
    run(['omarchy','theme','set','sonoma-glass'])
    store.commit({},history=False)
    run(['omarchy','theme','bg','set',store.THEME/'backgrounds'/values['desktop.wallpaper']])
    if a.with_login or a.with_boot:
        from cli import apply_system
        apply_system()
    print('Готово. Настройки: sonoma-glass configure · значок стекла в верхней панели.')
    print('Шрифт и фон Foot применяются к новым окнам. Резервная копия: '+str(backup))
