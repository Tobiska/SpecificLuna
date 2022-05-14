#include <cstdio>

#include "ucenv.h"

extern "C" {

void c_init(int arg0, OutputDF &arg1)
{
	arg1.setValue(arg0);
}

void c_show(const char* msg, int val) {
	printf("%s %d\n", msg, val);
}

}
