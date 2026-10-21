"""Persistent, validated settings and generated Omarchy configuration."""
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import tomllib

from schema import ROOT, DEFAULTS, INDEX, DOCUMENT, SCOPES, FIELDS

HOME = Path.home()
CONFIG = HOME / '.config/omarchy/sonoma-glass'
FILE = CONFIG / 'settings.json'
SUPPORT = HOME / '.local/share/sonoma-glass'
THEME = HOME / '.config/omarchy/themes/sonoma-glass'
CURRENT = HOME / '.local/state/omarchy/current/theme'
PLUGIN = SUPPORT / 'plugins/hyprglass-liquidjs.so'


def atomic(path, text):
    path = Path(path)
    if path.exists() and path.read_text() == text: return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as output:
            output.write(text)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def load():
    values = dict(DEFAULTS)
    if FILE.exists():
        saved = json.loads(FILE.read_text())
        values.update(validate(saved.get('values', saved)))
    return values


def validate(patch):
    if not isinstance(patch, dict): raise ValueError('Ожидался объект настроек')
    result = {}
    for key, value in patch.items():
        if key not in INDEX: raise ValueError('Неизвестная настройка: ' + key)
        item = INDEX[key]
        kind = item['type']
        if kind == 'boolean':
            if not isinstance(value, bool): raise ValueError(key + ': ожидается true/false')
        elif kind in ('number', 'integer'):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(key + ': ожидается конечное число')
            if value < item['min'] or value > item['max']:
                raise ValueError(f"{key}: диапазон {item['min']}…{item['max']}")
            if kind == 'integer':
                if value != int(value): raise ValueError(key + ': ожидается целое число')
                value = int(value)
        else:
            if not isinstance(value, str) or '\n' in value or '\r' in value or '\x00' in value or len(value) > 512:
                raise ValueError(key + ': недопустимая строка')
            if kind == 'color' and not re.fullmatch(r'#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?', value):
                raise ValueError(key + ': используйте #RRGGBB или #RRGGBBAA')
            if kind == 'color' and len(value)==9 and not item.get('alpha'):
                if value[-2:].lower()=='ff': value=value[:7]
                else: raise ValueError(key + ': используйте #RRGGBB; прозрачность настраивается отдельным параметром')
            if kind == 'choice' and value not in item['choices']:
                raise ValueError(key + ': допустимо ' + ', '.join(item['choices']))
            if kind == 'color': value = value.lower()
        result[key] = value
    return result


def parse(key, text):
    if key not in INDEX: raise ValueError('Неизвестная настройка: ' + key)
    kind = INDEX[key]['type']
    if kind == 'boolean':
        if text.lower() not in ('true', 'false', 'on', 'off', '1', '0'):
            raise ValueError('Используйте true/false или on/off')
        value = text.lower() in ('true', 'on', '1')
    elif kind in ('number', 'integer'): value = float(text)
    else: value = text
    return validate({key: value})[key]


def lua(value):
    if isinstance(value, dict):
        return '{ ' + ', '.join('['+json.dumps(key)+'] = '+lua(val) for key,val in value.items())+' }'
    if isinstance(value, list): return '{ ' + ', '.join(map(lua, value)) + ' }'
    if isinstance(value, bool): return 'true' if value else 'false'
    return json.dumps(value, ensure_ascii=True)


def rgba(color):
    return 'rgba(' + color[1:] + ('ff' if len(color) == 7 else '') + ')'


def hyprland(s):
    active = {'colors': [rgba(s['desktop.active_border']), 'rgba(ffffffaa)'], 'angle': 135}
    shadow = rgba(s['desktop.shadow_color']) if s['desktop.shadows'] else 'rgba(00000000)'
    config = {
        'general': {'gaps_in': s['desktop.gaps_in'], 'gaps_out': s['desktop.gaps_out'],
                    'border_size': s['desktop.border_size'], 'col': {'active_border': active, 'inactive_border': rgba(s['desktop.inactive_border'])}},
        'decoration': {'rounding': s['desktop.rounding'], 'rounding_power': s['desktop.rounding_power'],
            'shadow': {'enabled': True, 'range': s['desktop.shadow_range'], 'render_power': 3, 'color': shadow, 'color_inactive': shadow},
            'blur': {key.split('.',1)[1]: val for key,val in s.items() if key.startswith('blur.')}},
        'group': {'col': {'border_active': active, 'border_inactive': rgba(s['desktop.inactive_border'])}},
    }
    config['decoration']['blur']['new_optimizations'] = True
    out = ['-- Generated by sonoma-glass. Edit through CLI or the bar widget.', 'hl.config('+lua(config)+')']
    out.append('hl.window_rule('+lua({'match': {'class': '.*'}, 'opacity': f"{s['desktop.active_opacity']} {s['desktop.inactive_opacity']}"})+')')
    out.append('hl.window_rule('+lua({'match': {'class': 'foot'}, 'opacity': '1 1'})+')')
    namespaces = ['omarchy-bar','omarchy-menu','omarchy-emojis','omarchy-clipboard','omarchy-keyboard-panel','omarchy-osd','omarchy-notifications','omarchy-polkit','omarchy-network-qr']
    out.append('hl.layer_rule('+lua({'match': {'namespace': '^('+ '|'.join(namespaces) +')$'}, 'blur': s['blur.enabled'], 'ignore_alpha': .22})+')')
    if not PLUGIN.exists():
        return '\n'.join(out)+'\n'
    out += ['hl.plugin.load('+lua(str(PLUGIN))+')', 'local function configure_glass()', 'if not hl.plugin.hyprglass then return end', 'local hg = hl.plugin.hyprglass']
    names = {scope: ('liquidjs-' if s[f'glass.{scope}.model']=='liquidjs' else 'sonoma-')+scope for scope in SCOPES}
    out.append('hg.config('+lua({'enabled': s['components.glass'] and s['components.windows'],
        'default_theme': 'dark', 'default_preset': names['windows'], 'skip_opaque_windows': s['glass.common.skip_opaque'],
        'blur_fold': s['glass.common.blur_fold'],
        'manage_window_blur': True,
        'windows': {'background_cache': s['glass.common.background_cache'], 'live_resample': s['glass.common.windows_live'], 'live_resample_fps': s['glass.common.windows_fps']},
        'layers': {'enabled': s['components.glass'] and s['components.layers'],
                   'live_resample': s['glass.common.layers_live'], 'live_resample_fps': s['glass.common.layers_fps'], 'force_live_resample': s['glass.common.force_live']}})+')')
    for scope in SCOPES:
        preset = {'inherits': 'pomme'}
        for key in [f[0] for f in FIELDS]+['tint_color','fresnel_color','bevel_color','xray']:
            value = s[f'glass.{scope}.{key}']
            if key.endswith('_color'): value = int(value[1:]+('ff' if len(value)==7 else ''),16)
            preset[key] = value
        if scope=='terminal' and s['glass.terminal.model']=='liquidjs':
            preset['refraction_spread'] = s['terminal.rim_width']/96
        out.append('hg.preset('+lua(names[scope])+', '+lua(preset)+')')
    # Tags survive configuration reloads; remove old selections explicitly.
    for tag in ['hyprglass_preset_liquidjs-terminal','hyprglass_preset_sonoma-terminal','hyprglass_disabled']:
        out.append('hl.window_rule('+lua({'match': {'class': 'foot'}, 'tag': '-'+tag})+')')
    terminal_tag = '+hyprglass_preset_'+names['terminal'] if s['components.terminal'] else '+hyprglass_disabled'
    out.append('hl.window_rule('+lua({'match': {'class': 'foot'}, 'tag': terminal_tag})+')')
    for namespace in namespaces:
        scope = 'bar' if namespace=='omarchy-bar' else 'menu' if namespace in ['omarchy-menu','omarchy-emojis','omarchy-clipboard'] else 'widgets'
        layer={'preset': names[scope], **{k:s[f'glass.{scope}.{k}'] for k in ['mask_threshold','mask_feather','mask_mode']}}
        out.append('hg.layer('+lua(namespace)+', '+lua(layer if s[f'glass.{scope}.enabled'] else False)+')')
    out += ['end','configure_glass()', 'hl.on("hyprland.start", configure_glass)', 'hl.on("config.reloaded", configure_glass)']
    return '\n'.join(out)+'\n'


def toml_text(doc):
    lines=[]
    for section, values in doc.items():
        if isinstance(values,dict):
            lines.append('\n['+section+']')
            lines += [key+' = '+json.dumps(value,ensure_ascii=False) for key,value in values.items()]
        else: lines.append(section+' = '+json.dumps(values,ensure_ascii=False))
    return '\n'.join(lines)+'\n'


def theme_files(s):
    shell = tomllib.loads((ROOT/'templates/shell.toml').read_text())
    palette = tomllib.loads((ROOT/'templates/colors.toml').read_text())
    for key,value in s.items():
        if key.startswith('shell.'):
            _,section,name=key.split('.',2)
            shell[section][name]=value
        elif key.startswith('palette.'): palette[key[8:]]=value
    foot = '[colors-dark]\nalpha='+str(s['terminal.alpha'])+'\nalpha-mode=default\nblur='+('yes' if s['blur.enabled'] else 'no')+'\n'
    foot += 'foreground='+s['terminal.foreground'][1:7]+'\nbackground='+s['terminal.background'][1:7]+'\n'
    return {'hyprland.lua':hyprland(s), 'shell.toml':toml_text(shell), 'colors.toml':toml_text(palette),
            'foot.ini':foot, 'icons.theme':(ROOT/'templates/icons.theme').read_text() if s['components.icons'] else 'Adwaita\n'}


def active():
    name=HOME/'.local/state/omarchy/current/theme.name'
    return name.exists() and name.read_text().strip().lower().replace(' ','-')=='sonoma-glass'


def render(s, reload=True):
    files=theme_files(s)
    for name,text in files.items():
        atomic(THEME/name,text)
        if active(): atomic(CURRENT/name,text)
    foot = HOME/'.config/foot/foot.ini'
    if foot.exists() and active():
        text=foot.read_text()
        font=f"font={s['terminal.font']}:size={s['terminal.font_size']},JetBrainsMono Nerd Font:size={s['terminal.font_size']}"
        text=re.sub(r'^font\s*=.*$',lambda _:font,text,count=1,flags=re.M)
        if not re.search(r'^font\s*=',text,re.M): text=font+'\n'+text
        atomic(foot,text)
    if reload and active() and os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        subprocess.run(['hyprctl','reload'],check=True,capture_output=True,text=True)
        errors=subprocess.run(['hyprctl','configerrors'],check=True,capture_output=True,text=True).stdout.strip()
        if errors and errors!='ok': raise RuntimeError('Hyprland: '+errors)


def sync_components(s):
    """Switch existing clones without deleting user customisations."""
    path=HOME/'.config/omarchy/shell.json'
    if not path.exists(): return
    doc=json.loads(path.read_text())
    before=json_text(doc)
    disabled=set(doc.get('disabledPlugins',[]))
    user=os.environ.get('USER',HOME.name)
    for name in ('menu','lock'):
        clone=user+'.'+name
        if not (HOME/'.config/omarchy/plugins'/clone/'manifest.json').exists(): continue
        enabled=s['components.'+name]
        source='omarchy.'+name
        if enabled: disabled.add(source); disabled.discard(clone)
        else: disabled.discard(source); disabled.add(clone)
        for section in doc.get('bar',{}).get('layout',{}).values():
            for row in section:
                if row.get('id') in (source,clone): row['id']=clone if enabled else source
        for row in doc.get('plugins',[]):
            if row.get('id') in (source,clone): row['id']=clone if enabled else source
    doc['disabledPlugins']=sorted(disabled)
    after=json_text(doc)
    if before!=after: atomic(path,after)


def sync_icons(enabled):
    """Suspend only desktop entries owned by our icon installer."""
    suspended=SUPPORT/'disabled-icon-overrides.json'
    state=SUPPORT/'desktop-icon-overrides.json'
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
    if not enabled and not suspended.exists():
        saved=[]
        for item in json.loads(state.read_text()) if state.exists() else []:
            target=Path(item['target']); backup=Path(item['backup'])
            if not target.is_relative_to(HOME/'.local/share/applications') or not target.is_file(): continue
            contents=target.read_text()
            if item['created']: target.unlink()
            elif backup.is_file(): shutil.copy2(backup,target)
            else: continue
            saved.append({'target':str(target),'contents':contents,'restored_hash':digest(target)})
        atomic(suspended,json_text(saved))
    elif enabled and suspended.exists():
        for item in json.loads(suspended.read_text()):
            target=Path(item['target'])
            if target.is_relative_to(HOME/'.local/share/applications') and digest(target)==item['restored_hash']:
                atomic(target,item['contents'])
        suspended.unlink()
    if shutil.which('gsettings') and os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        theme=(ROOT/'templates/icons.theme').read_text().strip() if enabled else 'Adwaita'
        subprocess.run(['gsettings','set','org.gnome.desktop.interface','icon-theme',theme],check=True,capture_output=True)


def commit(patch, apply=True, history=True):
    patch=validate(patch)
    CONFIG.mkdir(parents=True,exist_ok=True)
    with (CONFIG/'settings.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        old=load()
        new={**old,**patch}
        if apply and new['components.icons'] and not (HOME/'.local/share/icons/SonomaGlass-dark/index.theme').exists():
            from installer import install_icons
            metadata=SUPPORT/'installation.json'
            if not metadata.exists(): raise RuntimeError('Сначала установите тему через install.sh')
            install_icons(Path(json.loads(metadata.read_text())['source']))
        if history and new!=old:
            history_dir=CONFIG/'history'
            history_dir.mkdir(exist_ok=True)
            atomic(history_dir/(str(time.time_ns())+'.json'),json_text({'version':1,'values':old}))
            for file in sorted(history_dir.glob('*.json'))[:-40]: file.unlink()
        try:
            # Persist only after Hyprland accepted the generated configuration.
            if apply: render(new)
            atomic(FILE,json_text({'version':1,'values':new}))
            atomic(CONFIG/'schema.json',json_text(DOCUMENT))
            if apply: sync_components(new)
            if apply and old['components.icons']!=new['components.icons']: sync_icons(new['components.icons'])
            if apply: atomic(CONFIG/'applied.json',json_text({'version':1,'values':new}))
        except Exception:
            if apply:
                with contextlib.suppress(Exception): render(old)
                if old['components.icons']!=new['components.icons']:
                    with contextlib.suppress(Exception): sync_icons(old['components.icons'])
            atomic(FILE,json_text({'version':1,'values':old}))
            raise
        if apply and active() and old['desktop.wallpaper']!=new['desktop.wallpaper']:
            wallpaper=THEME/'backgrounds'/new['desktop.wallpaper']
            if wallpaper.exists(): subprocess.run(['omarchy','theme','bg','set',str(wallpaper)],check=True)
    return new


_BASE_PRESET = {k:v for k,v in DEFAULTS.items() if k.startswith(('glass.','desktop.','terminal.alpha','bubbles.','blur.')) and k!='desktop.wallpaper'}
_BASE_PRESET.update({k:v for k,v in DEFAULTS.items() if k.startswith(('shell.bar.','shell.menu.','shell.popups.')) and k.endswith('background-alpha')})
_BASE_PRESET['components.bubbles']=True
PRESETS = {
    'balanced': dict(_BASE_PRESET),
    'clear': {**_BASE_PRESET,'desktop.active_opacity':.84,'desktop.inactive_opacity':.78,'terminal.alpha':.60,
              'shell.bar.background-alpha':.20,'shell.popups.background-alpha':.24,'shell.menu.background-alpha':.40},
    'frosted': {**_BASE_PRESET,'terminal.alpha':.78,'desktop.active_opacity':.93,'desktop.inactive_opacity':.88,
                **{f'glass.{scope}.blur_strength':1.8 for scope in SCOPES}},
    'quiet': {**_BASE_PRESET,'components.bubbles':False,**{f'glass.{scope}.refraction_strength':.40 for scope in SCOPES}},
}


def profile_path(name):
    if not re.fullmatch(r'[\w -]{1,64}',name): raise ValueError('Имя профиля: буквы, цифры, пробел, - или _')
    return CONFIG/'profiles'/(name+'.json')
