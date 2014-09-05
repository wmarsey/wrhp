#include <Python.h>
#include <iostream>
#include <cstring>
#include <stdlib.h>
#include "fastlevconst.hpp"
#include "fastlevhelp.hpp"	       
using namespace std;  

#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)));
#define MINFO(a, b, c) ((a) < (b) ? ((a) < (c) ? 1 : 3) : ((b) < (c) ? 2 : 3));
#define INT_DIGITS 19

#ifdef __cplusplus
extern "C" {
#endif

PyObject* weighteddistance(char *s1, char *s2){
  unsigned int s1len, s2len, i, j, yupflag = 0, xupflag = 0, c, pick;// iterations = 0;
  int yrelease = -1, xrelease = -1;
  Wint lastnum, oldnum, addw, delw, keepswapw;
  bool xtagmutex = false, ytagmutex = false;
  s1len = strlen(s1);
  s2len = strlen(s2);
  Wint column[s1len+1];

  //prepare Wints
  //preparewints(lastnum, oldnum, column, s1len+1);

  //initialise first column
  for (j = 1; j <= s1len; ++j)
    column[j].norm = column[j].w = j; //NEED TO INSERT TAG LOGIC HERE

  for (i = 1; i <= s2len; ++i) {    
    flagset(yrelease, ytagmutex, yupflag, s2, j-1);        

    //initialise head of column
    column[0].norm = column[0].w = i;  //NEED TO INSERT TAG LOGIC HERE?!
    
    for (j = 1, lastnum.w = i-1; j <= s1len; ++j){
      oldnum = column[j];
      flagset(xrelease, xtagmutex, xupflag, s1, i-1);

      c = (s1[j-1] == s2[i-1] ? 0 : 1);
      addw = column[j] + 1;
      delw = column[j-1] + 1;
      keepswapw = lastnum + c;
      column[j] = MIN3(addw, delw, keepswapw);
      pick = MINFO(addw, delw, keepswapw);
      
      //using flag logic to sum weightings
      flagsum(column[j], c, pick, ytagmutex, xtagmutex, yupflag, xupflag); 
      
      lastnum = oldnum;
      // ++iterations;
    }
  }

  //cout << iterations << endl;
  return winttopydict(column[s1len]);
}

int plaindistance(char *s1, char *s2) {
  unsigned int s1len, s2len, x, y, lastnum, oldnum;// iterations = 0;
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
      //++iterations;
    }
  }
  //cout << iterations << endl;
  return(column[s1len]);
}

static PyObject* fastlev_plaindist(PyObject *self, PyObject *args){ 
  char *x, *y;

  if (!PyArg_ParseTuple(args, "ss", &x, &y))
    return NULL;

  return Py_BuildValue("i", plaindistance(x, y));
}

static PyObject* fastlev_weightdist(PyObject *self, PyObject *args){ 
  char *x, *y;

  if (!PyArg_ParseTuple(args, "ss", &x, &y))
    return NULL;

  return Py_BuildValue("O", weighteddistance(x, y)); // THIS LINE MUST CHANGE
}

static PyMethodDef fastlev_methods[] = {
  {"plaindist", fastlev_plaindist, METH_VARARGS},
  {"weightdist", fastlev_weightdist, METH_VARARGS},
  {NULL, NULL}
};

void initfastlev(){
  (void) Py_InitModule("fastlev", fastlev_methods);
}

#ifdef __cplusplus
}
#endif
