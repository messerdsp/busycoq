// plain simulator: run exactly N steps from blank, print "DUMP state headpos cells" trimmed like tri's DUMP
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int c,char**v){const char*m=v[1];long N=atol(v[2]);int tw[6][2],tm[6][2],tn[6][2];
for(int s=0;s<6;s++)for(int y=0;y<2;y++){const char*t=m+s*7+y*3;if(t[0]=='-'){tn[s][y]=-1;continue;}tw[s][y]=t[0]-'0';tm[s][y]=t[1]=='R'?1:-1;tn[s][y]=t[2]-'A';}
long W=1L<<26;char*tp=calloc(W,1);long p=W/2;int s=0;
for(long i=0;i<N;i++){int y=tp[p];if(tn[s][y]<0){printf("HALT\n");return 0;}tp[p]=tw[s][y];p+=tm[s][y];s=tn[s][y];}
long a=0,b=W-1;while(a<p&&!tp[a])a++;while(b>p&&!tp[b])b--;
printf("DUMP %c %ld ",'A'+s,p-a);for(long i=a;i<=b;i++)putchar('0'+tp[i]);putchar('\n');}
