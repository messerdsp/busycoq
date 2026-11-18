import glob,re,sys
B=['010101','110101','011101','010111']; ROT=[B[r:]+B[:r] for r in range(4)]
rows=[]
for f in sorted(glob.glob(sys.argv[1]+'/v*_00.txt')):
    V=int(re.search(r'v(\d+)_00',f).group(1))
    t=open(f).read().split()[2:]
    # band: first stretch of >= 50 band words (any rotation)
    i=0
    while True:
        R=next((R for R in ROT if t[i:i+200]==R*50),None)
        if R: break
        i+=1
    cells_before=0; j=i
    # walk to the first run with count >= 100 after the band (the new top wall)
    while True:
        b,_,e=t[j].partition('^'); e=int(e) if e else 1
        if e>=100: W=e; break
        cells_before+=6*e; j+=1
    # total cells from band start to the next band (the following frozen unit), i.e. this frozen unit's size
    k=j; tot=cells_before
    while True:
        if any(t[k:k+200]==R*50 for R in ROT): break
        b,_,e=t[k].partition('^'); e=int(e) if e else 1; tot+=6*e; k+=1
    rows.append((V,cells_before,W,tot))
print('V  band_cells  band-8V/9*6  W  W-V/3  unit_cells  unit-(8V/9+4V/9)*6')
for V,c,W,tot in rows:
    print(V, c, round(c-48*V/9,2), W, round(W-V/3,2), tot, round(tot-8*V,2), 'V%3',V%3,'V%9',V%9,'V%4',V%4)
