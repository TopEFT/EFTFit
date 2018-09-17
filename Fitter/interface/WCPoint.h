#ifndef WCPOINT_H_
#define WCPOINT_H_

#include <iostream>
#include <sstream>
#include <iomanip>
#include <string>
#include <vector>
#include <unordered_map>

#include "split_string.h"

#include "TMath.h"

class WCPoint
{
public:
    std::unordered_map<std::string,double> inputs;  // {'c1': val, 'c2': val, ...}
    double wgt;
    std::string tag;

    WCPoint(){};

    WCPoint(std::string _str,double _wgt=0.0) {
        this->parseRwgtId(_str);
        this->wgt = _wgt;
        this->tag = _str;
    }

    ~WCPoint() {
        this->inputs.clear();
    }

    // Parses a rwgt string id, into the corresponding WC point
    void parseRwgtId(const std::string& _str) {
        // ex str: "EFTrwgt1_ctG_-1.2_ctW_2.4"
        std::vector<std::string> words;
        split_string(_str,words,"_");
        this->inputs.clear();
        for (uint i = 1; i < words.size(); i+= 2) {
            this->setStrength(words.at(i),std::stod(words.at(i+1)));
        }
    }

    void scale(double _val) {
        this->wgt *= _val;
    }

    // Explicity set a single WC parameter strength
    void setStrength(std::string wc_name,double strength) {
        this->inputs[wc_name] = strength;
    }

    // Sets all WCs to SM value (i.e. 0)
    void setSMPoint() {
        for (auto& kv: this->inputs) {
            this->inputs[kv.first] = 0.0;
        }
    }

    // Returns the strength for a particular WC, if the WC isn't found assume it to be 0 (SM value)
    double getStrength(std::string wc_name) {
        double strength = (this->inputs.find(wc_name) != this->inputs.end()) ? this->inputs.at(wc_name) : 0.0;
        return strength;
    }

    // Calculates the distance from the origin (SM point) using euclidean metric
    double getEuclideanDistance() {
        double d = 0.0;
        for (auto& kv: this->inputs) {
            d += TMath::Power(this->getStrength(kv.first),2);
        }
        d = TMath::Power(d,0.5);
        return d;
    }

    // Calculates the distance between WC points using euclidean metric
    double getEuclideanDistance(WCPoint* pt) {
        double d = 0.0;
        for (auto& kv: this->inputs) {
            d += TMath::Power((pt->getStrength(kv.first) - this->getStrength(kv.first)),2);
        }
        d = TMath::Power(d,0.5);
        return d;
    }


    // Returns the number of WC whose strength is non-zero
    double getDim() {
        int dim = 0;
        for (auto& kv: this->inputs) {
            if (kv.second != 0.0) {
                dim++;
            }
        }
        return dim;
    }

    // Returns if the point actually has an entry for a particular WC
    bool hasWC(std::string wc_name) {
        return (this->inputs.find(wc_name) != this->inputs.end());
    }

    // Compares if two WC points are equal
    bool isEqualTo(WCPoint* pt) {
        for (auto&kv: this->inputs) {
            if (pt->inputs.find(kv.first) == pt->inputs.end() && kv.second != 0.0) {
                // The other point is missing a WC (assumed to be 0)
                return false;
            } else if (pt->inputs[kv.first] != kv.second) {
                // The two points have different strengths for at least one WC
                return false;
            }
        }
        return true;
    }

    // Checks if the point is equal SM (i.e. 0 for all WC)
    bool isSMPoint() {
        for (auto &kv: this->inputs) {
            if (kv.second != 0.0) {
                return false;
            }
        }
        return true;
    }

    void dump(std::string _str="",bool append=false) {
        int padding = 15;
        std::stringstream ss1;
        std::stringstream ss2;

        ss1 << "wgt: " << std::setw(padding-5) << std::to_string(this->wgt);
        ss2 << std::setw(padding) << _str;
        for (auto& kv: this->inputs) {
            ss1 << std::setw(padding) << kv.first;
            ss2 << std::setw(padding) << std::to_string(kv.second);
        }

        if (!append) {
            std::cout << ss1.str() << std::endl;
        }
        std::cout << ss2.str() << std::endl;
    }
};

#endif
/* WCPOINT */