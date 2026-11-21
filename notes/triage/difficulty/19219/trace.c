// trace 19219 from a configuration: print every tick start "step n word" (word = pair bits), and the halt.
// usage: trace STATE HEAD CELLS MAXSTEPS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int c,char**v){const char*m="1RB1LD_1RC1RE_1LA0RA_1RC0LB_0LA1RF_---1RD";
int tw[6][2],tm[6][2],tn[6][2];for(int s=0;s<6;s++)for(int y=0;y<2;y++){const char*t=m+s*7+y*3;if(t[0]=='-'){tn[s][y]=-1;continue;}tw[s][y]=t[0]-'0';tm[s][y]=t[1]=='R'?1:-1;tn[s][y]=t[2]-'A';}
long W=1<<22;char*tp=calloc(W,1);int s=v[1][0]-'A';long head=atol(v[2]);const char*cells=v[3];long n0=strlen(cells),off=W/2-n0/2;
for(long i=0;i<n0;i++)tp[off+i]=cells[i]-'0';long p=off+head,lo=off,hi=off+n0;double N=atof(v[4]);
for(double i=0;i<N;i++){int y=tp[p];if(tn[s][y]<0){printf("HALT at step %.0f state %c, tape near head: ",i+1,'A'+s);for(long k=p-12;k<=p+12;k++)putchar(k==p?'[':'0'+tp[k]);putchar('\n');return 0;}
 tp[p]=tw[s][y];p+=tm[s][y];s=tn[s][y];if(p<lo)lo=p;if(p>hi)hi=p;
 if(s==0){long q=p-1; if(tp[q]!=1) continue; q--; long n=0; while(q-5>=lo-1 && tp[q]==0&&tp[q-1]==1&&tp[q-2]==1&&tp[q-3]==1&&tp[q-4]==1&&tp[q-5]==1){n++;q-=6;}
  if(!(tp[q]==0&&tp[q-1]==1&&tp[q-2]==1&&tp[q-3]==1)) continue; int ok=1; for(long k=lo;k<=q-4;k++) if(tp[k]){ok=0;break;} if(!ok)continue;
  long e=hi; while(e>p&&!tp[e])e--; if((e-p+1)%2) e++; int good=1; char buf[4096]; int bl=0;
  for(long k=p;k<=e;k+=2){ if(tp[k]!=1){good=0;break;} if(bl<4000) buf[bl++]='0'+tp[k+1]; } buf[bl]=0;
  if(good) printf("%.0f %ld %s\n",i+1,n,buf);}}
printf("RUN\n");}
