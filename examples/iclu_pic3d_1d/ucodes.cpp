#pragma once

#include "ucenv.h"

#include <iostream>

using namespace ucenv;

extern "C" {

void c_helloworld() {
	std::cout << "Hello world!!\n";
}

void c_init(OutputDF& n, OutputDF& sz) {
	n.setValue<int>(10);
	sz.setValue<int>(5);
}

void c_write_1(OutputDF& A, InputDF n, InputDF sz, InputDF l, InputDF r) {
	int* data = A.getData<int>();
	data[0] = l.getData<int>()[0];
	data[sz.getValue<int>()-1] = r.getData<int>()[0];
}

void c_read_1(InputDF A, InputDF n, InputDF sz, OutputDF& l, OutputDF& r) {
	const int* data = A.getData<int>();
	int* l_data = l.create<int>(1);
	int* r_data = r.create<int>(1);
	*l_data = data[1];
	*r_data = data[sz.getValue<int>()-2];
}

void c_write(OutputDF& A, InputDF n, InputDF sz, int i) {
	int* data = A.create<int>(sz.getValue<int>());
	for (int i = 0; i < sz.getValue<int>(); i++) {
		data[i] = i;
	}
}

void c_read(InputDF A, InputDF n, InputDF sz, int i) {
	const int* data = A.getData<int>();
	for (int i = 0; i < sz.getValue<int>(); i++) {
		std::cout << "[" << i << "]" << data[i] << "\n";
	}
}

void c_calc(InputDF Aprev, OutputDF& Anext, InputDF n, InputDF sz) {
	int* o_data = Anext.create<int>(sz.getValue<int>());
	const int* i_data = Aprev.getData<int>();
	for (int i = 0; i < sz.getValue<int>(); i++) {
		o_data[i] = i_data[i] + 1;
	}
}

void c_print(InputDF df) {
	std::cout << "DF: " << df.getValue<int>() << "\n";
}

}