#ifndef MOCK_NVECTOR_SERIAL_H
#define MOCK_NVECTOR_SERIAL_H
#define NV_Ith_S(v, i) (((double*)v)[i])
#define N_VNew_Serial(n) (void*)1
#define N_VDestroy_Serial(v)
#endif
