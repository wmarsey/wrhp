#ifndef FASTLEVHELP_HPP
#define FASTLEVHELP_HPP

#include <iostream>
using namespace std;

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

// void initialisewint(Wint &w){
//   w.w = 0;
//   w.norm = 0;
//   for(unsigned int i = 0; i < TAGNUM; ++i)
//     w.tags[i] = 0;
// } 

void winttolist(const Wint &wint, unsigned int *t){
  t[0] = wint.w;
  unsigned int i = 0;
  for( ; i < TAGNUM; ++i) t[i+1] = wint.tags[i];
  t[i+1] = wint.norm;
} 

bool testwint(const Wint &w){
  if(w.norm)
    return false;
  for(unsigned int i = 0; i < TAGNUM; ++i)
    if(w.tags[i])
      return false;
  return true;
}

bool indic(const char ch, const bool tagmutex){
  int vindex = (int)tagmutex;
  for(unsigned int i = 0; i < INDICNUM; ++i)
    if(ch == INDIC[vindex][i])
      return true;
  return false;
}

bool startwith(const char* str, const char* x){
  for(unsigned int i = 0; i < strlen(x); ++i)
    if (x[i] == '\0' || str[i] == '\0' || str[i] != x[i])
      return false;
  return true;
} 

int tagger(const char* str, unsigned int &upflag, const bool tagmutex){
  int vindex = (int)tagmutex;
  if (!tagmutex){
    for(unsigned int i = 0; i < TAGNUM; ++i)
      if(startwith(str, TAGS[i][vindex])){
        upflag = i;
	return 1;
    }
  } else {
    if(startwith(str, TAGS[upflag][vindex])){
      return strlen(TAGS[upflag][vindex]);
    }
  }
  return 0;
}

  void flagset(int &release, bool &tagmutex, unsigned int &upflag, const char* str, const unsigned int index){
  if(tagmutex && (release > 0)){
    --release;
  } else if (tagmutex && !release){
    tagmutex = false;
    release = -1;
    //final elif == !tagmutex || (tagmutex && release == -1)
  } else if(indic(str[index], tagmutex)){
    int tagq = tagger(str+index, upflag, tagmutex);
    if(tagq){
      if (tagmutex) release = tagq;
      else tagmutex = true;
    }
  }
}

void flagsum(Wint &wint, const bool &c, const unsigned int &pick, const bool &ytagmutex, const bool &xtagmutex, const unsigned int &yupflag, const unsigned int &xupflag){
  switch(pick){
  case 1: //add
    if(ytagmutex) //delete w\ flag
      ++wint.tags[yupflag];
    else if(c) //add w\o flag
      ++wint.norm;
    break;
  case 2: //delete
    if(xtagmutex) //delete w\ flag
      ++wint.tags[xupflag];
    else if(c) //delete w\o flag
      ++wint.norm;
    break;
  case 3: //keepswap
    if(c){
      if(ytagmutex) //swap w\ flag
	++wint.tags[yupflag];
      else //swap w\o flag
	++wint.norm;
    }
    break;
  }
}

// void preparewints(Wint &lastnum, Wint &oldnum, Wint *column, const unsigned int &len){
//   initialisewint(lastnum);
//   initialisewint(oldnum);  
//   for(unsigned int i = 0; i < len; ++i)
//     initialisewint(column[i]);
// }

#endif
