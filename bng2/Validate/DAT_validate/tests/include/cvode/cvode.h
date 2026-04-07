#ifndef MOCK_CVODE_H
#define MOCK_CVODE_H
#define realtype double
#define N_Vector void*
#define CV_BDF 1
#define CV_NEWTON 2
#define CV_NORMAL 1
typedef void* void_ptr;
#define CVodeCreate(a, b) (void*)1
#define CVodeFree(a)
#define CVodeInit(a, b, c, d) 0
#define CVodeSStolerances(a, b, c) 0
#define CVodeSetUserData(a, b) 0
#define CVodeSetMaxNumSteps(a, b) 0
#define CVodeSetMaxErrTestFails(a, b) 0
#define CVodeSetMaxConvFails(a, b) 0
#define CVodeSetMaxStep(a, b) 0
#define CVode(a, b, c, d, e) 0
#endif
