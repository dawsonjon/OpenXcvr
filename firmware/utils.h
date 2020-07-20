#ifndef __UTILS_H
#define __UTILS_H

//crude conversion to dBs
unsigned to_dB(unsigned x){
    unsigned dB = 0;
    while(x > 1){
        x >>= 1;
        dB += 6;
    }
    return dB;
}

//clamp a number between two values
unsigned clamp(unsigned a, unsigned b, unsigned c){
    if(a < b) return b;
    if(a > c) return c;
    return a;
}
#define MAX(a, b) a>b?a:b
#define MIN(a, b) a<b?a:b
#define clamp(a, b, c) MIN(c, MAX(a, b))

#endif
