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

unsigned max(unsigned x, unsigned y){
    if(x > y) return x;
    return y;
}
unsigned min(unsigned x, unsigned y){
    if(x < y) return x;
    return y;
}

unsigned clamp(unsigned x, unsigned min, unsigned max){
    if(x < min) return min;
    if(x > max) return max;
    return x;
}

#endif
