#ifndef FASTLEVCONST_HPP
#define FASTLEVCONST_HPP

const unsigned int INDICNUM = 3; //LENGTH OF LIST BELOW
char INDIC[][INDICNUM] = 
  {
    {'<', '{', '='},
    {'<', '}', ' '}
  };
const unsigned int TAGNUM = 17; //LENGTH OF TAGS
const unsigned int WINTLEN = TAGNUM + 2;
const char * TAGS[][2] = 
  {
    {"<math>", "</math>"}, //1
    {"<blockquote>", "</blockquote>"}, //2
    //{"= ", " ="}, 
    {"== ", " =="}, //3
    {"=== ", " ==="}, //4
    {"==== ", " ===="}, //5 
    {"===== ", " ====="}, //6
    {"====== ", " ======"}, //7
    {"{{math", "}}"}, //8
    {"[[", "]]"}, //9
    {"[http", "]"}, //10
    {"{{As of", "}}"}, //11
    {"[[media", "]]"}, //12
    {"<score>", "</score>"}, //13
    {"[[File", "]]"}, //14
    {"{|", "}"}, //15
    {"{{cite", "}}"}, //16
    {"{{Citation needed", "}}"} //17
  };
const char* TAGNAMES[TAGNUM] =
  {
    "maths1", //1 
    "blockquote", //2
    //"h1",  
    "h2", //3
    "h3", //4
    "h4", //5
    "h5", //6
    "h6", //7
    "maths2", //8
    "linkinternal", //9
    "linkexternal", //10
    "asof1", //11
    "media", //12
    "score", //13
    "file", //14
    "table", //15
    "citation", //16
    "citationneeded" //17
  };


class Wint {
public:
  unsigned int w;
  unsigned int tags [TAGNUM];
  unsigned int norm;
  Wint(){
    w = 0;
    norm = 0;
    for(unsigned int i = 0; i < TAGNUM; ++i)
      tags[i] = 0;
  }
};

#endif
