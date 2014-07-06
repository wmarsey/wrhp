#ifndef FASTLEVCONST_HPP
#define FASTLEVCONST_HPP

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

#endif
