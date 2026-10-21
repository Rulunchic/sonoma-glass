#!/usr/bin/env python3
"""Sonoma Glass: installer and the same settings used by the bar panel."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import settings as store
from schema import GROUPS, OPTIONS, INDEX, DOCUMENT


def choose(title, choices):
    if shutil.which('gum'):
        result=subprocess.run(['gum','choose','--header',title,*choices],text=True,capture_output=True)
        return result.stdout.strip() if result.returncode==0 else None
    print('\n'+title)
    for i, choice in enumerate(choices,1): print(f'{i}. {choice}')
    try: return choices[int(input('> '))-1]
    except (ValueError,IndexError,EOFError,KeyboardInterrupt): return None


def ask(title, value):
    if shutil.which('gum'):
        result=subprocess.run(['gum','input','--header',title,'--value',str(value)],text=True,capture_output=True)
        return result.stdout.rstrip('\n') if result.returncode==0 else None
    try: return input(f'{title} [{value}]: ') or str(value)
    except (EOFError,KeyboardInterrupt): return None


def configure(staged=False, initial=None):
    if not sys.stdin.isatty(): raise ValueError('Интерактивный режим требует терминал; используйте set или --yes')
    values=dict(initial) if initial is not None else store.load()
    changes={}
    while True:
        selected=choose('Sonoma Glass · настройки', [g['label'] for g in GROUPS]+['Готовые пресеты','Сохранить и выйти','Отмена'])
        if selected in (None,'Отмена'): return None
        if selected=='Сохранить и выйти':
            if not staged: store.commit(changes)
            return changes
        if selected=='Готовые пресеты':
            name=choose('Пресет',list(store.PRESETS))
            if name: changes.update(store.PRESETS[name]); values.update(store.PRESETS[name])
            continue
        group=next(g['id'] for g in GROUPS if g['label']==selected)
        while True:
            items=[o for o in OPTIONS if o['group']==group]
            labels=[o['label']+'  ·  '+str(values[o['key']]) for o in items]
            picked=choose(selected,labels+['Назад'])
            if picked in (None,'Назад'): break
            item=items[labels.index(picked)]
            key=item['key']
            if item['type']=='boolean': value=not values[key]
            elif item['type']=='choice':
                value=choose(item['label'],item['choices'])
                if value is None: continue
            else:
                text=ask(item['label']+(' · '+item['hint'] if item['hint'] else ''),values[key])
                if text is None: continue
                try: value=store.parse(key,text)
                except ValueError as e: print(e,file=sys.stderr); continue
            changes[key]=value
            values[key]=value


def parser():
    p=argparse.ArgumentParser(prog='sonoma-glass', description='Sonoma Glass — настройки темы, CLI и виджета')
    sub=p.add_subparsers(dest='command')
    sub.add_parser('configure',help='Интерактивные настройки')
    sub.add_parser('apply',help='Применить сохранённые настройки')
    sub.add_parser('status',help='Состояние и пути файлов')
    sub.add_parser('schema',help='JSON со всеми параметрами')
    sub.add_parser('list',help='Перечень параметров')
    g=sub.add_parser('get'); g.add_argument('key',nargs='?')
    s=sub.add_parser('set'); s.add_argument('key'); s.add_argument('value'); s.add_argument('--no-apply',action='store_true')
    j=sub.add_parser('set-json'); j.add_argument('json'); j.add_argument('--no-apply',action='store_true')
    pre=sub.add_parser('preset'); pre.add_argument('name',choices=list(store.PRESETS))
    sub.add_parser('undo',help='Вернуть предыдущие настройки')
    for name in ('export','import'):
        item=sub.add_parser(name); item.add_argument('file')
    profiles=sub.add_parser('profile'); profiles.add_argument('action',choices=['list','save','load','delete']); profiles.add_argument('name',nargs='?')
    wall=sub.add_parser('wallpaper'); wall.add_argument('name',nargs='?')
    system=sub.add_parser('system-apply',help='Применить экран входа/загрузки с правами администратора')
    system.add_argument('--gui',action='store_true')
    install=sub.add_parser('install',help='Установить / обновить компоненты')
    metadata=store.SUPPORT/'installation.json'
    source=json.loads(metadata.read_text()).get('source') if metadata.exists() else None
    install.add_argument('--source',type=Path,default=Path(source) if source else store.SUPPORT/'source')
    install.add_argument('--yes','-y',action='store_true')
    install.add_argument('--config',type=Path)
    install.add_argument('--set',action='append',default=[],metavar='KEY=VALUE')
    install.add_argument('--rebuild',action='store_true')
    install.add_argument('--refresh-icons',action='store_true')
    for component in ['glass','windows','layers','terminal','icons','menu','lock','buttons','bubbles']:
        install.add_argument('--no-'+component,action='store_true')
    install.add_argument('--with-login',action='store_true')
    install.add_argument('--with-boot',action='store_true')
    return p


def main():
    p=parser()
    a=p.parse_args()
    cmd=a.command or 'configure'
    if cmd=='configure': configure()
    elif cmd=='install':
        from installer import install
        install(a)
    elif cmd in ['get','schema','status','list']:
        values=store.load()
        if cmd=='schema': print(store.json_text(DOCUMENT),end='')
        elif cmd=='get': print(store.json_text(values if a.key is None else values[a.key]),end='')
        elif cmd=='list':
            for item in OPTIONS: print(f"{item['key']} = {values[item['key']]}  # {item['label']}")
        else:
            print(store.json_text({'active':store.active(),'settings':str(store.FILE),'widget':'sonoma.settings',
                                  'plugin':str(store.PLUGIN),'installed':store.PLUGIN.exists(),
                                  'parameters':len(OPTIONS),'system_pending':system_pending(values)}),end='')
    elif cmd in ['set','set-json','apply','preset']:
        patch={a.key:store.parse(a.key,a.value)} if cmd=='set' else json.loads(a.json) if cmd=='set-json' else store.PRESETS[a.name] if cmd=='preset' else {}
        store.commit(patch,apply=not getattr(a,'no_apply',False))
    elif cmd=='undo':
        files=sorted((store.CONFIG/'history').glob('*.json'))
        if not files: raise ValueError('Нет предыдущих настроек')
        previous=files[-1]
        store.commit(json.loads(previous.read_text())['values'],history=False)
        previous.unlink()
    elif cmd=='export': store.atomic(Path(a.file).expanduser(),store.json_text({'version':1,'values':store.load()}))
    elif cmd=='import':
        doc=json.loads(Path(a.file).expanduser().read_text())
        store.commit(doc.get('values',doc))
    elif cmd=='profile':
        if a.action=='list':
            print('\n'.join(p.stem for p in sorted((store.CONFIG/'profiles').glob('*.json'))))
        else:
            if not a.name: raise ValueError('Укажите имя профиля')
            path=store.profile_path(a.name)
            if a.action=='save': store.atomic(path,store.json_text({'version':1,'values':store.load()}))
            elif a.action=='load': store.commit(json.loads(path.read_text())['values'])
            else: path.unlink()
    elif cmd=='wallpaper':
        names=INDEX['system.wallpaper']['choices']
        name=a.name or choose('Обои',names)
        if name not in names: raise ValueError('Выберите: '+', '.join(names))
        store.commit({'desktop.wallpaper':name})
        subprocess.run(['omarchy','theme','bg','set',str(store.THEME/'backgrounds'/name)],check=True)
    elif cmd=='system-apply': apply_system(a.gui)


def system_values(values):
    return {k:v for k,v in values.items() if k.startswith('system.') or k in ('components.login','components.boot')}


def system_pending(values):
    path=store.CONFIG/'system-applied.json'
    return not path.exists() or json.loads(path.read_text())!=system_values(values)


def apply_system(gui=False):
    from installer import prepare_system
    prepare_system(store.load())
    command=['/usr/bin/python3',str(store.ROOT/'system-theme.py'),str(store.SUPPORT/'system-stage')]
    if os.geteuid()!=0: command.insert(0,'pkexec' if gui or not sys.stdin.isatty() else 'sudo')
    subprocess.run(command,check=True)
    store.atomic(store.CONFIG/'system-applied.json',store.json_text(system_values(store.load())))


if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,OSError,RuntimeError,subprocess.CalledProcessError) as error:
        print('Sonoma Glass: '+str(error),file=sys.stderr)
        sys.exit(1)
