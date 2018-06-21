#ifndef SPLITSTRING_H_
#define SPLITSTRING_H_

#include <string>
#include <boost/algorithm/string.hpp>

// See http://www.martinbroadhurst.com/how-to-split-a-string-in-c.html
template <class Container>
void split_string(const std::string& str, Container& cont, const std::string& delims = " ") {
    boost::split(cont,str,boost::is_any_of(delims));
}

#endif
/* SPLITSTRING */