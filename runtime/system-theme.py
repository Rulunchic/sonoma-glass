#!/usr/bin/python3
"""Apply greeter/splash settings explicitly, without restarting SDDM."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import tempfile

STATE = Path('/var/lib/sonoma-glass-settings')
SELECTOR = Path('/etc/sddm.conf.d/zz-sonoma-glass.conf')
PLYCONF = Path('/etc/plymouth/plymouthd.conf')
SDDM = Path('/usr/share/sddm/themes/sonoma-glass')
PLYMOUTH = Path('/usr/share/plymouth/themes/sonoma-glass')
SDDM_FILES = ['Main.qml','LiquidChrome.qml','liquid-control.frag','liquid-control.frag.qsb',
              'metadata.desktop','theme.conf','background.jpg']
PLY_FILES = ['sonoma-glass.plymouth','sonoma-glass.script','logo.png','bullet.png',
             'lock.png','entry.png','progress_box.png','progress_bar.png']


def snapshot(backup, path):
    if path.is_symlink(): raise RuntimeError('Unexpected symlink: '+str(path))
    if path.exists():
        dest=backup/str(path).lstrip('/')
        dest.parent.mkdir(parents=True,exist_ok=True)
        if path.is_dir(): shutil.copytree(path,dest)
        else: shutil.copy2(path,dest)


def restore(backup, path):
    if path.is_symlink(): raise RuntimeError('Unexpected symlink: '+str(path))
    saved=backup/str(path).lstrip('/')
    if saved.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(saved,path)
    else: path.unlink(missing_ok=True)


def publish(source,target,names):
    if target.is_symlink(): raise RuntimeError('Unexpected symlink: '+str(target))
    target.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.sonoma-',dir=target.parent))
    try:
        stage.chmod(0o755)
        for name in names:
            asset=source/name
            if not asset.is_file() or asset.is_symlink(): raise RuntimeError('Missing asset: '+str(asset))
            shutil.copyfile(asset,stage/name); (stage/name).chmod(0o644)
        if target.exists(): shutil.rmtree(target)
        os.replace(stage,target)
    finally:
        if stage.exists(): shutil.rmtree(stage)


def main():
    if os.geteuid()!=0: raise SystemExit('Administrator authentication is required')
    if len(sys.argv)!=2: raise SystemExit('Expected prepared asset directory')
    source=Path(sys.argv[1]).resolve()
    request=json.loads((source/'request.json').read_text())
    if any(type(request.get(k)) is not bool for k in ['login','boot','autologin']): raise ValueError('Invalid flags')
    user=pwd.getpwnam(request['user'])
    if user.pw_uid==0: raise ValueError('Root autologin is not supported')
    os.umask(0o022)
    STATE.mkdir(parents=True,exist_ok=True,mode=0o700)
    original=STATE/'original'
    if not original.exists():
        original.mkdir(mode=0o700)
        # Adopt selectors saved by the earlier local installer, if available.
        legacy=Path('/var/lib/sonoma-glass-startup/last-install.json')
        saved=None
        if legacy.exists():
            stamp=json.loads(legacy.read_text()).get('backup','')
            if stamp and '/' not in stamp: saved=legacy.parent/stamp
        for path in [SELECTOR,PLYCONF]:
            candidate=saved/str(path).lstrip('/') if saved else None
            if candidate and candidate.exists():
                dest=original/str(path).lstrip('/'); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(candidate,dest)
            elif path==SELECTOR and saved: pass
            else: snapshot(original,path)
    backup=STATE/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(mode=0o700)
    for path in [SELECTOR,PLYCONF]: snapshot(backup,path)
    previous_boot=PLYCONF.read_bytes() if PLYCONF.exists() else b''
    try:
        if request['login']:
            publish(source/'sddm',SDDM,SDDM_FILES)
            text='[Theme]\nCurrent=sonoma-glass\n'
        else:
            restore(original,SELECTOR)
            text=SELECTOR.read_text() if SELECTOR.exists() else ''
            # Remove old Autologin section before writing the requested policy.
            import re
            text=re.sub(r'(?ms)^\[Autologin\].*?(?=^\[|\Z)','',text)
        text+='\n[Autologin]\nUser='+ (user.pw_name if request['autologin'] else '')+'\n'
        if not request['autologin']: text+='Session=\n'
        text+='Relogin=false\n'
        SELECTOR.parent.mkdir(parents=True,exist_ok=True)
        SELECTOR.write_text(text); SELECTOR.chmod(0o644)
        if request['boot']:
            publish(source/'plymouth',PLYMOUTH,PLY_FILES)
            subprocess.run(['/usr/bin/plymouth-set-default-theme','sonoma-glass'],check=True)
        else: restore(original,PLYCONF)
        current_boot=PLYCONF.read_bytes() if PLYCONF.exists() else b''
        applied=STATE/'applied.json'
        old=json.loads(applied.read_text()) if applied.exists() else {}
        digest=hashlib.sha256(b''.join((source/'plymouth'/n).read_bytes() for n in PLY_FILES)).hexdigest()
        if previous_boot!=current_boot or (request['boot'] and digest!=old.get('splash_hash')):
            command='/usr/bin/limine-mkinitcpio' if Path('/usr/bin/limine-mkinitcpio').exists() else '/usr/bin/mkinitcpio'
            subprocess.run([command] if command.endswith('limine-mkinitcpio') else [command,'-P'],check=True)
        applied.write_text(json.dumps({**request,'splash_hash':digest,'backup':str(backup)},indent=2))
        applied.chmod(0o600)
    except Exception:
        for path in [SELECTOR,PLYCONF]: restore(backup,path)
        raise
    print('Экран входа и загрузки настроены. Изменения будут видны при следующем запуске.')
    print('Резервная копия системных настроек: '+str(backup))


if __name__=='__main__': main()
