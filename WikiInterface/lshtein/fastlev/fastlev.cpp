#include <Python.h>
#include <cstring>
using namespace std;  

#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)));
#define MINFO(a, b, c) ((a) < (b) ? ((a) < (c) ? 1 : 3) : ((b) < (c) ? 2 : 3));

#ifdef __cplusplus
extern "C" {
#endif


int plaindistance(char *s1, char *s2) {
  unsigned int s1len, s2len, x, y, lastnum, oldnum;
  s1len = strlen(s1);
  s2len = strlen(s2);
  unsigned int column[s1len+1];
  for (y = 1; y <= s1len; y++)
    column[y] = y;
  for (x = 1; x <= s2len; x++) {
    column[0] = x;
    for (y = 1, lastnum = x-1; y <= s1len; y++) {
      oldnum = column[y];
      column[y] = MIN3(column[y] + 1, //add 
		       column[y-1] + 1, //del
		       lastnum + (s1[y-1] == s2[x-1] ? 0 : 1)); //keepswap
      lastnum = oldnum;
    }
  }
  return(column[s1len]);
}

static PyObject* fastlev_plaindist(PyObject *self, PyObject *args){ 
  char *x, *y;

  if (!PyArg_ParseTuple(args, "ss", &x, &y))
    return NULL;

  return Py_BuildValue("i", plaindistance(x, y));
}
static PyMethodDef fastlev_methods[] = {
  {"plaindist", fastlev_plaindist, METH_VARARGS},
  {NULL, NULL}
};

void initfastlev(){
  (void) Py_InitModule("fastlev", fastlev_methods);
}

#ifdef __cplusplus
}
#endif
