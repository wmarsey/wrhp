#include <Python.h>
#include <iostream>
#include <vector>
#include <cstring>
#include <regex.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>	       
using namespace std;  

#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)))
#define INT_DIGITS 19

#ifdef __cplusplus
extern "C" {
#endif

const unsigned int INDICNUM = 3;
char INDIC[] = {'<', '{', '}'};
const unsigned int TAGNUM = 2;
const unsigned int WINTLEN = TAGNUM + 2;
const char * TAGS[][2] = 
  {
    {"<math>", "</math>"},
    {"<blockquote>", "</blockquote>"}
  };

struct Wint {
  unsigned int w;
  unsigned int tags [TAGNUM];
  unsigned int norm;
};

void winttolist(Wint wint, unsigned int *t){
  t[0] = wint.w;
  cout << wint.w << endl;
  unsigned int i = 0;
  for( ; i < TAGNUM; ++i){
    t[i+1] = wint.tags[i];
    cout << wint.tags[i] << endl;
  }
  t[i+1] = wint.norm;
  cout << wint.norm << endl;
} 

// char* itoa(unsigned int i){
//   static char buf[INT_DIGITS + 2];
//   char *p = buf + INT_DIGITS + 1;
//   if (i >= 0) {
//     do {
//       *--p = '0' + (i % 10);
//       i /= 10;
//     } while (i != 0);
//   }
//   else {
//     do {
//       *--p = '0' - (i % 10);
//       i /= 10;
//     } while (i != 0);
//     *--p = '-';
//   } 
//   return p;
// }

// unsigned int numdig(unsigned int n){
//     int d = 0;
//     if (n < 0) d = 1;
//     while (n) {
//         n /= 10;
//         d++;
//     }
//     return d;
// }

bool operator<(const Wint& X, const Wint& Y){
  return X.w < Y.w;
}

Wint operator+(const Wint &W, const int &C){
  Wint n = W;
  ++n.w;
  return n;
}

ostream& operator<<(ostream& o, const Wint x){
  o << "[" << x.w << ", ";
  for(unsigned int i = 0; i < TAGNUM; ++i)
    o << x.tags[i] << ", ";
  o << x.norm << "]" << endl;
  return o;
}

bool indic(char ch){
  for(unsigned int i = 0; i < INDICNUM; ++i)
    if(ch == INDIC[i])
      return true;
  return false;
}

bool startwith(char* str, const char* x){
  for(unsigned int i = 0; i < strlen(x); ++i)
    if (x[i] == '\0' || str[i] == '\0' || str[i] != x[i])
      return false;
  return true;
} 

bool tagger(char* str, unsigned int &tagi, unsigned int &tagv){
  for(unsigned int v = 0; v < 2; ++v){
    for(unsigned int i = 0; i < TAGNUM; ++i){
      if(startwith(str, TAGS[i][v])){
	tagi = i;
	tagv = v;
	return true;
      }
    }
  }
  return false;
}

PyObject* weighteddistance(char *s1, char *s2){
  unsigned int s1len, s2len, i, j, tagsemaphore = 0;;
  Wint lastnum, oldnum;
  s1len = strlen(s1);
  s2len = strlen(s2);
  Wint column[s1len+1];
  bool xflags[] = {
    false, 
    false
  };
  bool yflags[] = {
    false, 
    false
  }; 

  //prepare column of Wints
  for(unsigned int u = 0; u < s1len+1; ++u)
    for(unsigned int v = 0; v < TAGNUM; ++v)
      column[u].tags[v] = 0;
  for (j = 1; j <= s1len; j += 2)
    column[j].w = j;

  for (i = 1; i <= s2len; ++i) {
    
    //second string flags
    if(indic(s2[i-1])){
      unsigned int tagi = 0, tagv = 0;
      if(tagger(s2+i-1, tagi, tagv)){
	  if (tagv){
	    cout << "recieved1 " << tagi << "," << tagv << endl;
	    yflags[tagi] = false;
	    --tagsemaphore;
	  }else{
	    yflags[tagi] = true;
	    ++tagsemaphore;
	  }
      }
    }

    column[0].w = i;
    for (j = 1, lastnum.w = i-1; j <= s1len; ++j){
      oldnum = column[j];

      //first string flags
      if(indic(s1[j-1])){
	unsigned int tagi = 0, tagv = 0;
	if(tagger(s2+i-1, tagi, tagv)){ //returns [tagnum,stop?]
	  cout << "recieved2 " << tagi << "," << tagv << endl;
	  if (tagv){
	    cout << tagi << endl;
	    xflags[tagi] = false;
	    --tagsemaphore;
	  } else{
	    xflags[tagi] = true;
	    ++tagsemaphore;
	  }
	}
      }

      //minimum selector
      column[j] = MIN3(column[j] + 1, 
			 (column[j-1]) + 1, 
			 lastnum + (s1[j-1] == s2[i-1] ? 0 : 1));
      
      for(unsigned int p = 0; p < TAGNUM; ++p)
	if(xflags[p] or yflags[p])
	  ++column[j].tags[p];
      if(!tagsemaphore)
	++(column[j].norm);
      
      lastnum = oldnum;
    }
  }

  cout << column[s1len];


  PyObject* result = PyList_New(TAGNUM+2);
  unsigned int rawresults[WINTLEN];
  winttolist(column[s1len], rawresults);
  if (!result) cout << "result list not created" << endl;
  for(unsigned int i = 0; i < TAGNUM + 2; ++i){
    cout << (long)rawresults[i] << endl;
    PyObject* number = PyInt_FromLong((long)rawresults[i]);
    PyList_SetItem(result, i, number);
  }
    
  return result;
}

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
