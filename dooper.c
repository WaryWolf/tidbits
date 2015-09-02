/*
    ==============================

    dooper.c - Anthony Vaccaro (aka WaryWolf, aka pem), 2015

    This doop heens its way around argv[0]
    and looks cool in "top", "ps" and similar programs.
    You will have to press "c" in top to see the result.
    "d1<Enter>" is also recommended.

    compile like this:

    gcc -Wall -std=gnu99 -pthread -o dooper dooper.c -lm

    ==============================
*/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <math.h>


void rotate(char* str);
void rotate_str( char* dest, char* src, int offset);
void* cpuload(void* arg);


int main (int argc, char** argv) {

    char* coolstr;

    pthread_t loadthread;
    int arg = strlen(argv[0]);
    int offset = 0;



    coolstr = (char*)malloc(sizeof(char) * 255);
    coolstr = "THIS IS MY HEENER. THERE ARE MANY LIKE IT BUT THIS ONE IS MINE. \0";

    // clear out argv[0] 
    for(int i = 0; i < arg; i++) {
        argv[0][i] = ' ';
    }

    pthread_create(&loadthread, NULL, cpuload, NULL);


    while(1) {

        rotate_str(argv[0], coolstr, offset);
        offset += sizeof(char);

        
        // for debugging
        printf("%d - %s\n",(int)strlen(argv[0]),argv[0]);
        
        sleep(1);
    

    }
    
    return 0;
}

// copies a portion of src into dest. If offset + strlen(dest) > strlen(src), then there is not enough to copy into
// dest, and the remaining characters will be copied from the beinning of src instead.
// don't try to use this with a dest larger than src, it might not work.
void rotate_str( char* dest, char* src, int offset) {



    int extra = 0;
    int srclen = strlen(src);
    int destlen = strlen(dest);


    // this lets us wrap around forever
    offset = offset % srclen;

    if (destlen > srclen) {
        fprintf(stderr, "argv[0] is too long for this string, exiting before we break something...\n");
        exit(1);
    }

    strncpy(dest, src + offset, destlen);


    // if needed, fill the end of dest with the start of src
    if (offset + destlen > srclen) {
        extra = (offset + destlen) - srclen;
        strncpy(dest + (destlen - extra), src, extra);
    }
}

// rotates (in-place) the given string by one character. uses a temporary buffer. no return.
void rotate( char* str) {

    int len = strlen(str);
    
    char* buf = (char*)malloc(sizeof(char) * (len + 2));

    buf[len+1] = '\0';

    strncpy(buf+1, str, len - 1);

    buf[0] = str[len - 1];

    strncpy(str, buf, len);
    
    free(buf);
}

// makes the cpu hot.
void* cpuload(void* arg) {

    while(1) {
        sqrt(rand());
    }
    return NULL;
}
