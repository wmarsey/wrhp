#include <Python.h>
#include <iostream>
#include <vector>
#include <cstring>
#include <regex.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>	       
using namespace std;  

#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)));
#define MINFO(a, b, c) ((a) < (b) ? ((a) < (c) ? 1 : 3) : ((b) < (c) ? 2 : 3));
#define INT_DIGITS 19

#ifdef __cplusplus
extern "C" {
#endif

const unsigned int INDICNUM = 3; //LENGTH OF LIST BELOW
char INDIC[][INDICNUM] = 
  {
    {'<', '{', '='},
    {'<', '}', ' '}
  };
const unsigned int TAGNUM = 19; //LENGTH OF TAGS
const unsigned int WINTLEN = TAGNUM + 2;
const char * TAGS[][2] = 
  {
    {"<math>", "</math>"},
    {"<blockquote>", "</blockquote>"},
    {"= ", " ="},
    {"== ", " =="},
    {"=== ", " ==="},
    {"==== ", " ===="},
    {"===== ", " ====="},
    {"====== ", " ======"},
    {"{{math", "}}"},
    {"[[", "]]"},
    {"[http", "]"},
    {"{{As of", "}}"},
    {"[[media", "]]"},
    {"<score>", "</score>"},
    {"[[File", "]]"},
    {"{|", "}"},
    {"{{cite", "}}"},
    {"{{Citation needed", "}}"}
  };
const char* TAGNAMES[TAGNUM] =
  {
    "maths1",
    "blockquote",
    "h1", 
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "maths2",
    "linkinternal",
    "linkexternal",
    "asof1",
    "media",
    "score",
    "file",
    "table",
    "citation",
    "citationneeded"
  };
    

struct Wint {
  unsigned int w;
  unsigned int tags [TAGNUM];
  unsigned int norm;
};


bool operator<(const Wint &x, const Wint &y){
  return x.w < y.w;
}

Wint operator+(const Wint &w, const int &c){
  Wint n = w;
  n.w += c;
  return n;
}

ostream& operator<<(ostream& o, const Wint &x){
  o << "[" << x.w << ", ";
  for(unsigned int i = 0; i < TAGNUM; ++i)
    o << x.tags[i] << ", ";
  o << x.norm << "]" << endl;
  return o;
}

void initialisewint(Wint &w){
  w.w = 0;
  w.norm = 0;
  for(unsigned int i = 0; i < TAGNUM; ++i)
    w.tags[i] = 0;
} 

void winttolist(Wint &wint, unsigned int *t){
  t[0] = wint.w;
  unsigned int i = 0;
  for( ; i < TAGNUM; ++i) t[i+1] = wint.tags[i];
  t[i+1] = wint.norm;
} 

bool testwint(Wint &w){
  if(w.norm)
    return false;
  for(unsigned int i = 0; i < TAGNUM; ++i)
    if(w.tags[i])
      return false;
  return true;
}

bool indic(char ch, bool tagmutex){
  int vindex = (int)tagmutex;
  for(unsigned int i = 0; i < INDICNUM; ++i)
    if(ch == INDIC[vindex][i])
      return true;
  return false;
}

bool startwith(char* str, const char* x){
  for(unsigned int i = 0; i < strlen(x); ++i)
    if (x[i] == '\0' || str[i] == '\0' || str[i] != x[i])
      return false;
  return true;
} 

bool tagger(char* str, unsigned int &upflag, bool tagmutex){
  int vindex = (int)tagmutex;
  if (!tagmutex){
    for(unsigned int i = 0; i < TAGNUM; ++i)
      if(startwith(str, TAGS[i][vindex])){
        upflag = i;
	return true;
    }
  } else {
    if(startwith(str, TAGS[upflag][vindex])){
      return true;
    }
  }
  return false;
}

PyObject* weighteddistance(char *s1, char *s2){
  unsigned int s1len, s2len, i, j, yupflag = 0, xupflag = 0;
  Wint lastnum, oldnum;
  bool xtagmutex = false, ytagmutex = false;;
  s1len = strlen(s1);
  s2len = strlen(s2);
  Wint column[s1len+1];

  //prepare Wints
  initialisewint(lastnum);
  initialisewint(oldnum);  
  for(unsigned int i = 0; i < s1len+1; ++i)
    initialisewint(column[i]);

  for (j = 1; j <= s1len; j += 2){
    column[j].w = j;
    //NEED TO INSERT TAG LOGIC HERE
  }

  //MAIN OUTER LOOP
  for (i = 1; i <= s2len; ++i) {
    
    //flag and mutex setting, string 2
    if(indic(s2[i-1], ytagmutex)){
      if(tagger(s2+i-1, yupflag, ytagmutex)){
	if (ytagmutex) ytagmutex = false;
	else ytagmutex = true;
      }
    }

    column[0].w = i;
    //NEED TO INSERT TAG LOGIC HERE

    //MAIN INNER LOOP
    for (j = 1, lastnum.w = i-1; j <= s1len; ++j){
      oldnum = column[j];

      //flag and mutex setting, string 1
      if(indic(s1[j-1], xtagmutex)){
	if(tagger(s1+j-1, xupflag, xtagmutex)){
	  if (xtagmutex) xtagmutex = false;
	  else xtagmutex = true;
	}
      }
      
      //minimum selector
      unsigned int c = (s1[j-1] == s2[i-1] ? 0 : 1);
      Wint aw = column[j] + 1;
      Wint bw = column[j-1] + 1;
      Wint cw = lastnum + c;
      column[j] = MIN3(aw, bw, cw);
      unsigned int pick = MINFO(aw, bw, cw);
      
      // if(!testwint(column[j])){
      // 	cout << "wint spoilt iteration " << i << "," << j << endl;
      // 	cout << " comparing characters " << s1[j-1] << "," << s2[i-1] << endl;
      // 	cout << " which should be the same as " << *(s1+j-1) << "," << *(s2+i-1) << endl;
      // 	if (xtagmutex)
      // 	  cout << " with x mutex up, tag index " << xupflag << endl;
      // 	if (ytagmutex)
      // 	  cout << " with y mutex up, tag index " << yupflag << endl;
      // 	cout << "the Wints in the column are" << endl;
      // 	for(unsigned int d = 0; d < s1len+1; ++d)
      // 	  cout << column[d];
      // 	cout << "oldnum is " << endl;
      // 	cout << oldnum;
      // 	cout << "lastnum is " << endl;
      // 	cout << lastnum;
      // 	exit(-1);
      // }
      
      if(c || (pick != 3)){
	if(xtagmutex or ytagmutex){
	  if (yupflag == xupflag){
	    ++column[j].tags[yupflag];
	  } else {
	    ++column[j].tags[yupflag];
	    ++column[j].tags[xupflag];
	  }
	}
      } else if (pick != 3){
	++column[j].norm;
      }
      
      lastnum = oldnum;
    }
  }

  //construct python list of results
  PyObject* result = PyList_New(WINTLEN);
  unsigned int rawresults[WINTLEN];
  winttolist(column[s1len], rawresults);
  if (!result) cout << "result list not created" << endl;
  for(unsigned int i = 0; i < WINTLEN; ++i){
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
