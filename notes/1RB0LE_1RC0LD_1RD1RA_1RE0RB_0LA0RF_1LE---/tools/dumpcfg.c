/* Dump configurations of a 6-state machine every EVERY steps (cell by cell, simulated).
   Output per sample: step state dir_of_last_move then left half (far->head) and right half (head->far), as
   run-length strings "a:n,a:n,...".  Usage: dumpcfg MACHINE START_STATE STEPS EVERY */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N (1<<25)
static unsigned char tape[N];
int main(int argc,char**argv){
  const char*m=argv[1]; int st=argv[2][0]-'A'; long long steps=atoll(argv[3]), every=atoll(argv[4]);
  int W[6][2],D[6][2],S[6][2];
  for(int i=0;i<6;i++)for(int b=0;b<2;b++){const char*c=m+7*i+3*b; if(c[2]<'A'||c[2]>'F'){S[i][b]=-1;continue;}
    W[i][b]=c[0]-'0'; D[i][b]=c[1]=='R'?1:-1; S[i][b]=c[2]-'A';}
  long long pos=N/2, lo=pos, hi=pos; int last=1;
  for(long long t=0;t<steps;t++){
    int b=tape[pos];
    if(S[st][b]<0){printf("HALT %lld\n",t);return 0;}
    if(t%every==0){
      printf("%lld %c %c ",t,'A'+st,last>0?'R':'L');
      long long a=lo; while(a<pos&&tape[a]==0)a++;
      long long i=a; while(i<pos){long long j=i; while(j<pos&&tape[j]==tape[i])j++; printf("%d:%lld,",tape[i],j-i); i=j;}
      printf(" | ");
      long long e=hi; while(e>=pos&&tape[e]==0)e--;
      i=pos; while(i<=e){long long j=i; while(j<=e&&tape[j]==tape[i])j++; printf("%d:%lld,",tape[i],j-i); i=j;}
      printf("\n");
    }
    tape[pos]=W[st][b]; last=D[st][b]; pos+=last; st=S[st][b];
    if(pos<lo)lo=pos; if(pos>hi)hi=pos;
    if(pos<2||pos>N-3){printf("OUT\n");return 1;}
  }
  return 0;
}
