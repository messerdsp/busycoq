// print tick starts of 19219 from blank: state A, tape = 0^inf 1110 (111110)^n 1 A> word 0^inf (pairs 1b)
// output: step n bits
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int c,char**v){const char*m="1RB1LD_1RC1RE_1LA0RA_1RC0LB_0LA1RF_---1RD";long N=atol(v[1]);long every=c>2?atol(v[2]):1;
int tw[6][2],tm[6][2],tn[6][2];for(int s=0;s<6;s++)for(int y=0;y<2;y++){const char*t=m+s*7+y*3;if(t[0]=='-'){tn[s][y]=-1;continue;}tw[s][y]=t[0]-'0';tm[s][y]=t[1]=='R'?1:-1;tn[s][y]=t[2]-'A';}
long W=1<<24;char*tp=calloc(W,1);long p=W/2,lo=p,hi=p;int s=0;long cnt=0;
for(long i=0;i<N;i++){int y=tp[p];if(tn[s][y]<0){printf("HALT %ld\n",i);return 0;}tp[p]=tw[s][y];p+=tm[s][y];s=tn[s][y];if(p<lo)lo=p;if(p>hi)hi=p;
 if(s==0){ // check left side: ...0 1110 (111110)^n 1 [p]
  long q=p-1; if(tp[q]!=1) continue; q--; long n=0; while(q-5>=lo-1 && tp[q]==0&&tp[q-1]==1&&tp[q-2]==1&&tp[q-3]==1&&tp[q-4]==1&&tp[q-5]==1){n++;q-=6;}
  if(!(tp[q]==0&&tp[q-1]==1&&tp[q-2]==1&&tp[q-3]==1)) continue; long z=q-4; int ok=1; for(long k=lo;k<=z;k++) if(tp[k]){ok=0;break;} if(!ok)continue;
  // word: pairs from p to last 1
  long e=hi; while(e>p&&!tp[e])e--; if((e-p+1)%2) e++; int good=1; char buf[100000]; int bl=0;
  for(long k=p;k<=e;k+=2){ if(tp[k]!=1){good=0;break;} if(bl<99990) buf[bl++]='0'+tp[k+1]; } buf[bl]=0;
  if(!good) continue; if(cnt++%every==0) printf("%ld %ld %s\n",i+1,n,bl>80?buf+bl-80:buf);
 }}
}
