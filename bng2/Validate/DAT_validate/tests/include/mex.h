#ifndef MOCK_MEX_H
#define MOCK_MEX_H

#ifdef __cplusplus
extern "C" {
#endif

#define mxArray void
extern void mexPrintf(const char* fmt, ...);
extern void mexErrMsgTxt(const char* err);
extern int mxGetM(const void* pm);
extern int mxGetN(const void* pm);
extern double* mxGetPr(const void* pm);
extern void* mxCreateDoubleMatrix(int m, int n, int ComplexFlag);
#define mxREAL 0

#ifdef __cplusplus
}
#endif

#endif
