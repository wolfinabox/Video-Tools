import subprocess
import sys,os
uic_exe=sys.argv[1] if len(sys.argv)>1 else r'./env/scripts/pyside2-uic'
app_dir=sys.argv[2] if len(sys.argv)>2 else r'./app'
for f in os.listdir(app_dir):
    if os.path.splitext(f)[1]!='.ui': continue
    comm=f'{uic_exe} {os.path.join(app_dir,f)} -o {os.path.splitext(os.path.join(app_dir,f))[0]}.py'
    print(comm)
    subprocess.call(comm)