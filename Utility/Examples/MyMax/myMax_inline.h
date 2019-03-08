
#ifndef MY_MAX_H
#define MY_MAX_H MY_MAX_H

#ifdef DECLARATION
INLINE int myMax( int a, int b );
#endif

#ifdef DEFINITION
INLINE int myMax( int a, int b ) {
  return a > b ? a : b;
}
#endif

#endif
