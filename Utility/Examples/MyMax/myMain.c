
#include <stdio.h>

#include "myMax_inline.h"

extern int useMyMax( int a, int b );
extern int otherUse( int a, int b );

int main() {

  int a = 2;
  int b = 3;

  int res;

  res = myMax( a, b );
  printf( "%d\n", res );

  res = useMyMax( a, b );    
  printf( "%d\n", res );

  res = otherUse( a, b );
  printf( "%d\n", res );

  return 0;
  
}
