#ifndef WCFIT_H_
#define WCFIT_H_

#include <iostream>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <string>
#include <vector>
#include <tuple>    // for std::pair

#include "WCPoint.h"
#include "split_string.h"

#include "TMatrixD.h"
#include "TVectorD.h"
#include "TDecompSVD.h"

class WCFit
{
private:
    // Using vectors here instead of map to ensure ordering
    std::vector<std::pair<std::string,std::string> > names;
    std::vector<double> values; // The fit structure constants
    std::vector<WCPoint> points;
    std::string tag;    // Names the fit, for identification
    WCPoint start_pt;

    int kPad = 12;

public:
    WCFit(){
        this->tag = "";
    }

    WCFit(std::vector<WCPoint> pts,std::string _tag) {
        this->points = pts;
        this->fitPoints(this->points);
        this->setTag(_tag);
    }

    ~WCFit(){
        this->clear();
    }

    std::string kSMstr = "sm";    // Need to figure out how to make this a global constant...

    void setTag(std::string _tag) {
        this->tag = _tag;
    }

    // Specify the MadGraph starting point
    void setStart(WCPoint pt) {
        this->start_pt = pt;
    }

    void setStart(std::string id_tag, double wgt_val) {
        this->start_pt = WCPoint(id_tag,wgt_val);
    }

    std::string getTag() {
        return this->tag;
    }

    WCPoint getStart() {
        return this->start_pt;
    }

    std::vector<std::pair<std::string,std::string> > getNames() {
        return this->names;
    }

    // Returns a particular structure constant from the fit function
    double getParameter(std::string n1, std::string n2) {
        for (uint i = 0; i < this->names.size(); i++) {
            if (n1 == this->names.at(i).first && n2 == this->names.at(i).second) {
                return this->values.at(i);
            } else if (n1 == this->names.at(i).second && n2 == this->names.at(i).first) {
                return this->values.at(i);
            }
        }
        // We don't have this fit parameter, assume 0 (i.e. SM value)
        return 0.0;
    }

    // Overloaded function for quickly getting a specific structure constant
    double getParameter(uint idx) {
        if (idx >= this->values.size()) {
            std::cout << "[ERROR] Tried to access invalid index for WC Fit, " << idx << std::endl;
            throw;
        }
        return this->values.at(idx);
    }

    // Returns the lowest strength for a particular WC from among all fit points
    double getLowStrength(std::string wc_name) {
        if (this->points.size() == 0) {
            return 0.0;
        } else if (this->points.size() == 1) {
            return this->points.at(0).getStrength(wc_name);
        }
        double strength = this->points.at(0).getStrength(wc_name);
        for (uint i = 1; i < this->points.size(); i++) {
            if (this->points.at(i).getStrength(wc_name) < strength) {
                strength = this->points.at(i).getStrength(wc_name);
            }
        }
        return strength;
    }

    // Returns the largest strength for a particular WC from among all fit points
    double getHighStrength(std::string wc_name) {
        if (this->points.size() == 0) {
            return 0.0;
        } else if (this->points.size() == 1) {
            return this->points.at(0).getStrength(wc_name);
        }
        double strength = this->points.at(0).getStrength(wc_name);
        for (uint i = 1; i < this->points.size(); i++) {
            if (this->points.at(i).getStrength(wc_name) > strength) {
                strength = this->points.at(i).getStrength(wc_name);
            }
        }
        return strength;
    }

    // Checks to see if the fit includes the specified WC
    bool hasCoefficient(std::string wc_name) {
        for (uint i = 0; i < this->names.size(); i++) {
            if (wc_name == this->names.at(i).first || wc_name == this->names.at(i).second) {
                return true;
            }
        }
        return false;
    }

    // Evaluate the fit at a particular WC phase space point
    double evalPoint(WCPoint* pt) {
        double val = 0.0;
        for (uint i = 0; i < this->names.size(); i++) {
            std::string n1 = this->names.at(i).first;
            std::string n2 = this->names.at(i).second;

            double x1,x2;
            if (n1 == kSMstr) {
                x1 = 1.0;
            } else if (pt->inputs.find(n1) != pt->inputs.end()) {
                x1 = pt->inputs.at(n1);
            } else {
                // If the WCPoint did not specify a WC, assume its strength is 0 (i.e. SM value)
                x1 = 0.0;
            }

            if (n2 == kSMstr) {
                x2 = 1.0;
            } else if (pt->inputs.find(n2) != pt->inputs.end()) {
                x2 = pt->inputs.at(n2);
            } else {
                // If the WCPoint did not specify a WC value, assume its strength is 0 (i.e. SM value)
                x2 = 0.0;
            }

            double fit_constant = this->values.at(i);    // This is the structure constant
            val += x1*x2*fit_constant;
        }
        return val;
    }

    // Changes a specific structure constant by the specified amount, if none found adds it to the list
    void addParameter(std::string n1, std::string n2, double amt) {
        for (uint i = 0; i < this->names.size(); i++) {
            if (n1 == this->names.at(i).first && n2 == this->names.at(i).second) {
                this->values.at(i) += amt;
                return;
            } else if (n1 == this->names.at(i).second && n2 == this->names.at(i).first) {
                this->values.at(i) += amt;
                return;
            }
        }
        // The structure constant doesn't exist in our fit, add it and set its value to amt
        auto pair = std::make_pair(n1,n2);
        this->names.push_back(pair);
        this->values.push_back(amt);
    }

    // Extract a n-Dim quadratic fit from a collection of WC phase space points
    void fitPoints(std::vector<WCPoint> pts) {
        this->names.clear();
        this->values.clear();

        if (pts.size() == 0) {
            // No points to fit!
            return;
        }

        std::vector<std::string> wc_coeffs = { kSMstr };   // This vector controls the ordering of our phase space point
        for (auto& kv: pts.at(0).inputs) {
            wc_coeffs.push_back(kv.first);
        }

        uint nDim  = wc_coeffs.size() - 1;
        uint nCols = 1 + 2*nDim + nDim*(nDim - 1)/2;
        uint nRows = pts.size();

        TMatrixD A(nRows,nCols);
        TVectorD b(nRows);

        for (uint row_idx = 0; row_idx < nRows; row_idx++) {
            uint col_idx = 0;
            for (uint i = 0; i < wc_coeffs.size(); i++) {
                for (uint j = 0; j < wc_coeffs.size(); j++) {
                    if (i > j) {
                        // Don't double count
                        continue;
                    }

                    if (row_idx == 0) {
                        // On first pass, initialize names of the structure constants
                        auto pair = std::make_pair(wc_coeffs.at(i),wc_coeffs.at(j));
                        this->names.push_back(pair);
                    }

                    std::string s1,s2;
                    double v1,v2;
                    s1 = wc_coeffs.at(i);
                    s2 = wc_coeffs.at(j);
                    v1 = ((s1 == kSMstr) ? 1.0 : pts.at(row_idx).inputs[s1]);  // Hard set SM value to 1.0
                    v2 = ((s2 == kSMstr) ? 1.0 : pts.at(row_idx).inputs[s2]);  // Hard set SM value to 1.0

                    A(row_idx,col_idx) = v1*v2;
                    b(row_idx) = pts.at(row_idx).wgt;
                    col_idx++;
                }
            }
        }

        TDecompSVD svd(A);
        bool ok;
        const TVectorD c_x = svd.Solve(b,ok);    // Solve for the fit parameters

        for (uint i = 0; i < this->names.size(); i++) {
            this->values.push_back(c_x(i));
            //std::cout << this->names.at(i).first << "*" << this->names.at(i).second << ": " << c_x(i) << std::endl;
        }
    }

    // Add the structure constants from one fit to this fit
    void addFit(WCFit added_fit) {
        auto added_names = added_fit.getNames();
        for (uint i = 0; i < added_names.size(); i++) {
            double amt = added_fit.getParameter(i);
            this->addParameter(added_names.at(i).first,added_names.at(i).second,amt);
        }
    }

    void scale(double _val) {
        for (uint i = 0; i < this->values.size(); i++) {
            this->values.at(i) = this->values.at(i)*_val;
        }
    }

    // Wipes the fit information
    void clear() {
        this->names.clear();
        this->values.clear();
        this->points.clear();
    }

    // Save the fit to indicated file
    void save(std::string fpath,bool append=false) {
        if (!append) {
            std::cout << "Producing fitparams table..." << std::endl;
        }

        std::stringstream ss1;  // Header info
        std::stringstream ss2;  // Row info

        ss1 << std::setw(kPad) << "";
        ss2 << std::setw(kPad) << this->tag;
        for (uint i = 0; i < this->names.size(); i++) {
            std::string n1 = this->names.at(i).first;
            std::string n2 = this->names.at(i).second;

            ss1 << std::setw(kPad) << n1+"*"+n2;
            ss2 << std::setw(kPad) << std::to_string(this->values.at(i));
        }

        std::ofstream outf;
        if (append) {
            outf.open(fpath,std::ofstream::app);
        } else {
            outf.open(fpath,std::ofstream::out | std::ofstream::trunc);
            outf << ss1.str();
        }
        outf << "\n" << ss2.str();
        outf.close();

        this->dump(append);
    }

    // Same as save, but dumps to stdout instead
    void dump(bool append=false,uint max_cols=13) {
        std::stringstream ss1;  // Header info
        std::stringstream ss2;  // Row info

        ss1 << std::setw(kPad+5) << "";
        ss2 << std::setw(kPad+5) << this->tag;
        for (uint i = 0; i < this->names.size(); i++) {
            if (i >= max_cols) {
                break;
            }
            std::string n1 = this->names.at(i).first;
            std::string n2 = this->names.at(i).second;

            ss1 << std::setw(kPad) << n1+"*"+n2;
            ss2 << std::setw(kPad) << std::to_string(this->values.at(i));
        }

        if (!append) {
            std::cout << ss1.str() << std::endl;
        }
        std::cout << ss2.str() << std::endl;
    }
};

#endif
/* WCFIT */