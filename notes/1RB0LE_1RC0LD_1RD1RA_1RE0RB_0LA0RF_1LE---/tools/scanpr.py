import subprocess,re,sys
sys.path.insert(0,sys.argv[1]); from canon import canon
targets={'23154':'1RB0LE_1RC0LD_1RD1RA_1RE0RB_0LA0RF_1LE---','115779':'1RB0LC_1RC1RE_1RD0RA_0LE0RF_1RA0LD_1LD---','TM567':'1RB0RD_0LC0RF_1RD0LB_1RE0LA_1RA1RC_1LB---','third':'1RB---_0RC0LA_1LD0RB_1LE0RF_1LF1LC_1LB0LD'}
tc={canon(v):k for k,v in targets.items()}
print(tc)
pat=re.compile(r'[01][LR][A-F]|---')
tm=re.compile(r'(?:(?:[01][LR][A-Z]|---){2}_){5}(?:[01][LR][A-Z]|---){2}')
refs=subprocess.run(['git','for-each-ref','--format=%(refname:short)','refs/remotes/pr/'],capture_output=True,text=True).stdout.split()
refs.append('origin/BB6')
for r in refs:
    base='origin/BB6' if r!='origin/BB6' else 'origin/BB6~0'
    if r=='origin/BB6':
        txt=subprocess.run(['git','grep','-h','-o','-E','([01][LR][A-Z]|---){2}(_([01][LR][A-Z]|---){2}){5}',r],capture_output=True,text=True).stdout
        txt+=subprocess.run(['git','log','--format=%B',r],capture_output=True,text=True).stdout
    else:
        mb=subprocess.run(['git','merge-base','origin/BB6',r],capture_output=True,text=True).stdout.strip()
        txt=subprocess.run(['git','diff',mb,r],capture_output=True,text=True,errors='replace').stdout
        txt+=subprocess.run(['git','log','--format=%B',f'{mb}..{r}'],capture_output=True,text=True).stdout
    found=set()
    for m in tm.findall(txt):
        try: c=canon(m)
        except Exception: continue
        if c in tc: found.add((tc[c],m))
    for k,v in targets.items():
        if v in txt: found.add((k,'literal'))
    if found: print(r,sorted(found))
print('done',len(refs))
