#include <string>
#include <vector>
#include <list>
#include <unordered_map>
#include <map>
#include <iostream>

#include "TString.h"
#include "TText.h"
#include "TPad.h"

#include "RooArgSet.h"
#include "RooLinkedListIter.h"
#include "RooRealVar.h"
#include "RooAbsData.h"

#include "split_string.h"
#include "AnalysisCategory.h"

/*// See: https://root-forum.cern.ch/t/width-of-a-tlatex-text/20961/13
// Note: This segaults if it reaches the 'else' block...
UInt_t GetTextWidth(TText *t) {
   UInt_t w,h;
   Int_t f = t->GetTextFont();

   if (f%10<=2) {
      t->GetTextExtent(w,h,t->GetTitle());
   } else {
      w = 0;
      TText t2 = *t;
      t2.SetTextFont(f-1);
      TVirtualPad *pad = gROOT->GetSelectedPad();
      if (!pad) return w;
      Float_t dy = pad->AbsPixeltoY(0) - pad->AbsPixeltoY((Int_t)(t->GetTextSize()));
      Float_t tsize = dy/(pad->GetY2() - pad->GetY1());
      t2.SetTextSize(tsize);
      t2.GetTextExtent(w,h,t2.GetTitle());
   }
   return w;
}*/

// Should return a string padded on left and right to give a centered string (if possible)
TString centerTStr(TString str, int width) {
    TString s = str;
    if (s.Length() >= width) {
        return s;
    }
    int tpad = width - s.Length();  // The total amount of padding we have to work with
    int lpad = tpad / 2;    // Padding to add to the right of the string
    int rpad = tpad - lpad; // Padding to add to the left of the string
    s = TString::Format("%*s%s%*s",lpad,"",s.Data(),rpad,"");
    return s;
}

// Get sub-set of a vector [i1,i2)
template<typename T>
std::vector<T> vector_slice(std::vector<T> const &v, uint i1, uint i2) {
    // Out of range check
    if (i2 > v.size()) i2 = v.size();
    // Ordering check
    if (i1 > i2) i1 = (i2 > 0) ? (i2 - 1) : i2;

    auto first = v.cbegin() + i1;
    auto last = v.cbegin() + i2;
    std::vector<T> ret(first,last);
    return ret;
}

void iter_print(RooArgSet set,Int_t contents) {
    RooAbsArg *next = 0;
    RooFIter it = set.fwdIterator();
    while ((next=it.next())) {
        TString name = next->GetName();
        // if (!name.Contains("C_2lss_p_ee_2b_4j")) {
        //    continue;
        // } else if (!name.Contains("ttH")) {
        //    continue;
        // }

        // if (!name.BeginsWith("pdfbins_binC")) {
        //    continue;
        // }

        // if (!name.BeginsWith("pdf_binC_")) {
        //    continue;
        // }

        if (name.BeginsWith("n_exp_binC_")) {
            continue;
        }

        // if (name != "CMS_fakeObs") {
        //    continue;
        // }

        RooRealVar* rrv = dynamic_cast<RooRealVar *>(next);

        // next->printClassName(std::cout); std::cout << "::";
        // std::cout << name << std::endl;

        // next->Print();
        rrv->Print();
        rrv->getBinning().printArgs(std::cout); std::cout << std::endl;
        rrv->getBinning().printTitle(std::cout);

        std::cout << "Bins: " << rrv->getBinning().numBins() << std::endl;
        std::cout << "Err: " << rrv->getError() << std::endl;

        // next->Print("s");
        // next->Print("t");
        // next->Print("v");
        // next->printMultiline(std::cout,contents);
        // next->printTree(std::cout);
        // std::cout << "------------------------------------------------------------------------------" << std::endl;
    }
}

void iter_print(std::list<RooAbsData*> lst,Int_t contents) {
    for (auto d: lst) {
        TString name = d->GetName();
        std::cout << name << std::endl;
        d->Print();
        d->printMultiline(std::cout,contents);
    }
}

// // Sets the value of the RooRealVar based on 'type'
// void set_rrv(RooRealVar* rrv, TString type, double sigma) {
//     rrv->removeRange();
//     double nom_var  = rrv->getVal();
//     double down_var = rrv->getVal() + rrv->getErrorLo()*sigma;
//     double up_var   = rrv->getVal() + rrv->getErrorHi()*sigma;
//     if (type == "up") {
//         // Sets the rrv to the up fluct*sigma
//         rrv->setVal(up_var);
//     } else if (type == "down") {
//         // Sets the rrv to the down fluct*sigma
//         rrv->setVal(down_var);
//     } else if (type == "nom") {
//         // Sets the rrv to a specific value
//         rrv->setVal(sigma);
//     }
// }

// void set_rrv(TString name, RooArgSet& arg_set, TString type, double sigma) {
//     RooRealVar* rrv = (RooRealVar*)arg_set.find(name);
//     if (!rrv) {
//         std::cout << "Unknown RRV: " << name << std::endl;
//         return;
//     }
//     set_rrv(rrv,type,sigma);
// }

// Prints various values for a single RooRealVar
void print_rrv(RooRealVar* rrv, RooFitResult& fr) {
    const char* indent = "  ";
    std::string name = rrv->GetName();
    double nom_var  = rrv->getVal();
    TString fstr = "";
    fstr += TString::Format("RRV %s\n",rrv->GetName());
    fstr += TString::Format("%sVal: %.2f +/- %.2f\n",indent,rrv->getVal(),rrv->getError());
    // fstr += TString::Format("%sErr: %.2f\n",indent,rrv->getError());
    fstr += TString::Format("%s(ErrLo,ErrHi):   (%.2f,%.2f)\n",indent,rrv->getErrorLo(),rrv->getErrorHi());
    fstr += TString::Format("%s(AsymLo,AsymHi): (%.2f,%.2f)\n",indent,rrv->getAsymErrorLo(),rrv->getAsymErrorHi());
    fstr += TString::Format("%sPropErr: %.2f\n",indent,rrv->getPropagatedError(fr));
    fstr += TString::Format("%sRange: [%.2f,%.2f]",indent,rrv->getMin(),rrv->getMax());
    std::cout << fstr << std::endl;

    // std::cout << "RRV " << rrv->GetName() << ":"
    //           << "\n  Val: "     << rrv->getVal()
    //           << "\n  Err: "     << rrv->getError()
    //           << "\n  Lo:  "     << rrv->getErrorLo()
    //           << "\n  Hi:  "     << rrv->getErrorHi()
    //           << "\n  AsymLo: "  << rrv->getAsymErrorLo()
    //           << "\n  AsymHi: "  << rrv->getAsymErrorHi()
    //           << "\n  PropErr: " << rrv->getPropagatedError(fr)
    //           << std::endl;
}

// Prints a single RRV from the given RooArgSet
void print_rrv(TString name, RooArgSet& arg_set, RooFitResult& fr) {
    RooRealVar* rrv = (RooRealVar*)arg_set.find(name);
    if (!rrv) {
        std::cout << "Unknown RRV: " << name << std::endl;
        return;
    }
    print_rrv(rrv,fr);
}

// Print various values for each element in the RooArgSet
void print_all_rrv(RooArgSet pois, RooFitResult& fr) {
    RooLinkedListIter iterP = pois.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        print_rrv(rrv,fr);
    }
}

// Prints the yields for categories which have been summed over certain processes
template<typename T>
void print_yields(std::vector<T> yields, RooFitResult& fr) {
    TString indent = "    ";

    std::cout << "Yields:" << std::endl;
    int dMax = 0;
    for (auto y: yields) {
        TString n = y->GetName();
        dMax = (dMax > n.Length()) ? dMax : n.Length();
    }

    for (auto y: yields) {
        TString n  = y->GetName();
        double val = y->getVal();
        double err = y->getPropagatedError(fr);

        std::cout << indent << std::left << std::setw(dMax) << n << ": "
                  << std::setw(8) << val << " +/- "
                  << std::setw(9) << err << std::endl;
    }
}

void printNuisParams(RooArgList lst) {
    int w1 = 0;
    int w2 = 0;
    int w3 = 0;
    int sz = 0;
    std::string str;
    for (int i = 0; i < lst.getSize(); i++) {
        RooRealVar const* rrv = dynamic_cast<RooRealVar const*>(lst.at(i));
        str  = rrv->GetName();
        sz = str.size();
        w1 = TMath::Max(w1,sz);

        str = std::to_string(rrv->getVal());
        sz  = str.size();
        w2  = TMath::Max(w2,sz);

        str = "(" + std::to_string(rrv->getErrorLo()) + "," + std::to_string(rrv->getErrorLo()) + ")";
        sz  = str.size();
        w3  = TMath::Max(w3,sz);

    }
    std::cout << TString::Format("%*s : %*s +/- %*s %s",-1*w1,"Name",-1*w2,"Nominal",-1*w3," Asym. Error","Sym. Error") << std::endl;
    for (int i = 0; i < lst.getSize(); i++) {
        RooRealVar const* rrv = dynamic_cast<RooRealVar const*>(lst.at(i));
        std::string name = rrv->GetName();
        double nom_val = rrv->getVal();
        double err = rrv->getError();
        double err_d = rrv->getErrorLo();
        double err_u = rrv->getErrorHi();
        str = "(" + std::to_string(err_d) + "," + std::to_string(err_u) + ")";
        std::cout << std::left << std::setw(w1) << name << " : "
                  << std::right << std::setw(w2) << std::to_string(nom_val)
                  << " +/- " << std::left << std::setw(w3) << str
                  << " " << err
                  << std::endl;
    }
}

void printPOICorrelations(RooArgSet pois, RooFitResult* fr) {
    int counter = 0;
    auto it1 = pois.createIterator();
    for (RooRealVar* rrv1 = (RooRealVar*) it1->Next(); rrv1 != 0; rrv1 = (RooRealVar*) it1->Next()) {
        auto it2 = pois.createIterator();
        std::string n1 = rrv1->GetName();
        for (RooRealVar* rrv2 = (RooRealVar*) it2->Next(); rrv2 != 0; rrv2 = (RooRealVar*) it2->Next()) {
            std::string n2 = rrv2->GetName();
            double corr_val = fr->correlation(n1.c_str(),n2.c_str());
            //double corr_val = fr->correlation(&rrv1,&rrv2);
            std::string s1 = " <" + n1 + "," + n2 + "> ";
            std::string s2 = std::to_string(corr_val);
            if (corr_val > 0) {
                s2 = " " + s2;
            }
            std::cout << std::left << std::setw(15) << s1 << s2 << std::endl;
            counter++;
        }
        //std::cout << std::endl;
    }
}

void printLatexYieldTable(std::vector<AnalysisCategory*> cats, std::vector<TString> sgnls, std::vector<TString> bkgds, RooFitResult* fr, std::unordered_map<std::string,std::string> bin_labels, std::unordered_map<std::string,std::string> yield_labels) {
    std::string cr = "\\\\";            // carrige return
    std::string col    = " & ";         // column identifier
    std::string hline  = "\\hline";     // insert horizontal line

    bool for_paper = false;  // Changes the sig figs of the output for use in the AN or Paper
    bool skip_header = false;

    TString last_bkgd_name, last_sgnl_name;
    TString bkgd_sum_name = "Sum Bkgd.";
    TString sgnl_sum_name = "Sum Sgnl.";
    TString tot_exp_name = "Total Exp.";
    TString data_name = "Data";

    if (for_paper) {
        skip_header = true;
        bkgd_sum_name = "Sum Background";
        sgnl_sum_name = "Sum Signal";
        tot_exp_name = "Total Expected";
    }

    std::vector<int> col_widths(cats.size()+1,0);   // The +1 is for the process name column
    std::vector<double> sum_bkgds(cats.size(),0);
    std::vector<double> sum_sgnls(cats.size(),0);

    std::vector<std::vector<TString> > rows;
    std::vector<TString> row;

    ////////////////////////////////////////////////
    // Add in a header row
    ////////////////////////////////////////////////
    if (!skip_header) {
        row.clear();
        row.push_back("");
        col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
        for (uint i=0; i < cats.size(); i++) {
            AnalysisCategory* cat = cats.at(i);
            TString str = cat->getName();
            if (bin_labels.count(str.Data())) {
                str = bin_labels[str.Data()];
            }
            col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
            row.push_back(str);
        }
        rows.push_back(row);
    }

    ////////////////////////////////////////////////
    // Add in the background process rows
    ////////////////////////////////////////////////
    for (uint i=0; i < bkgds.size(); i++) {
        row.clear();
        TString proc = bkgds.at(i);
        TString row_name = proc;
        if (for_paper) {
            if (yield_labels.count(proc.Data())) {
                row_name = yield_labels[proc.Data()];
            }
            last_bkgd_name = row_name;
        }
        row.push_back(row_name);
        col_widths.at(0) = std::max(col_widths.at(0),row_name.Length());

        for (uint j=0; j < cats.size(); j++) {
            AnalysisCategory* cat = cats.at(j);
            double val = cat->getExpProc(proc);
            TString str = TString::Format("%.2f",val);
            if (for_paper) {
                str = TString::Format("%.1f",val);
            }
            sum_bkgds.at(j) += val;
            row.push_back(str);
            col_widths.at(j+1) = std::max(col_widths.at(j+1),str.Length());
        }
        rows.push_back(row);
    }

    row.clear();
    row.push_back(bkgd_sum_name);
    col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
    for (uint i=0; i < sum_bkgds.size(); i++) {
        double val = sum_bkgds.at(i);
        TString str = TString::Format("%.2f",val);
        if (for_paper) {
            str = TString::Format("%.1f",val);
        }
        row.push_back(str);
        col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
    }
    rows.push_back(row);

    ////////////////////////////////////////////////
    // Add in the signal process rows
    ////////////////////////////////////////////////
    for (uint i=0; i < sgnls.size(); i++) {
        row.clear();
        TString proc = sgnls.at(i);
        TString row_name = proc;
        if (for_paper) {
            if (yield_labels.count(proc.Data())) {
                row_name = yield_labels[proc.Data()];
            }
            last_sgnl_name = row_name;
        }
        row.push_back(row_name);
        col_widths.at(0) = std::max(col_widths.at(0),row_name.Length());

        for (uint j=0; j < cats.size(); j++) {
            AnalysisCategory* cat = cats.at(j);
            double val = cat->getExpProc(proc);
            TString str = TString::Format("%.2f",val);
            if (for_paper) {
                str = TString::Format("%.1f",val);
            }
            sum_sgnls.at(j) += val;
            row.push_back(str);
            col_widths.at(j+1) = std::max(col_widths.at(j+1),str.Length());
        }
        rows.push_back(row);
    }

    row.clear();
    row.push_back(sgnl_sum_name);
    col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
    for (uint i=0; i < sum_sgnls.size(); i++) {
        double val = sum_sgnls.at(i);
        TString str = TString::Format("%.2f",val);
        if (for_paper) {
            str = TString::Format("%.1f",val);
        }
        row.push_back(str);
        col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
    }
    rows.push_back(row);

    ////////////////////////////////////////////////
    // Add in the total expected row
    ////////////////////////////////////////////////
    row.clear();
    row.push_back(tot_exp_name);
    col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
    for (uint i=0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        double val = cat->getExpSum();
        double err = cat->getExpSumError(fr);
        TString str = TString::Format("%.2f \\pm %.2f",val,err);
        if (for_paper) {
            str = TString::Format("$%.0f \\pm %.0f$",val,err);
        } else {
            // Only update the col widths here b/c this row is an outlier in terms of length
            col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
        }
        row.push_back(str);
    }
    rows.push_back(row);

    ////////////////////////////////////////////////
    // Add in the data observed row
    ////////////////////////////////////////////////
    row.clear();
    row.push_back(data_name);
    col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
    for (uint i=0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        double val = cat->getData();
        TString str = TString::Format("%.0f",val);
        col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
        row.push_back(str);
    }
    rows.push_back(row);

    ////////////////////////////////////////////////
    // Construct the entire table row-by-row
    ////////////////////////////////////////////////
    std::stringstream ss;
    for (uint i=0; i < rows.size(); i++) {
        std::vector<TString> row = rows.at(i);
        for (uint j=0; j < row.size(); j++) {
            TString entry = row.at(j);
            int colw = col_widths.at(j);

            if (j == 0) { // left-justify
                ss << TString::Format("%*s",-1*colw,entry.Data());
            } else { // right-justify
                ss << TString::Format("%*s",colw,entry.Data());
            }
            if (j < row.size() - 1) {
                ss << col;
            } else {
                ss << " " << cr;
            }
        }
        if (for_paper) {
            // Add in the \hline for latex
            if (row.at(0) == bkgd_sum_name  || row.at(0) == sgnl_sum_name ||
                row.at(0) == tot_exp_name   || row.at(0) == data_name ||
                row.at(0) == last_bkgd_name || row.at(0) == last_sgnl_name) {
                ss << " " << hline;
            }
        }
        ss << "\n";
    }
    std::cout << ss.str() << std::endl;
}

// Iterates over the RooArgSet and sets their values to +/- values based on 'type'
void adjustRRVs(
    RooArgSet pois,
    TString type,
    double sigma=1.0,
    std::set<std::string> skip={},
    std::set<std::string> keep={}
) {
    RooLinkedListIter iterP = pois.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        std::string name = rrv->GetName();
        rrv->removeRange();     // We don't care about limiting the range of values at this point
        if (skip.size() && skip.count(name)) {
            continue;
        }
        if (keep.size() && !keep.count(name)) {
            continue;
        }
        double nom_var  = rrv->getVal();
        double down_var = rrv->getVal() + rrv->getErrorLo()*sigma;
        double up_var   = rrv->getVal() + rrv->getErrorHi()*sigma;
        //std::cout << name << " Up: " << up_var << std::endl;
        if (type == "up") {
            rrv->setVal(up_var);
        } else if (type == "down") {
            rrv->setVal(down_var);
        } else if (type == "nom") {
            rrv->setVal(nom_var);
        } else {
            rrv->setVal(nom_var);
        }
    }
}

// Sets the specified RRV to the specified value
void setRRV(RooArgSet pois, std::string name, double val) {
    RooLinkedListIter iterP = pois.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        std::string rrv_name = rrv->GetName();
        if (rrv_name != name) continue;
        rrv->setVal(val);
    }
}

// Sets the RooRealVar error values
void setRRVError(RooArgSet pois, std::string name, double val_hi, double val_lo=0.0) {
    RooLinkedListIter iterP = pois.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        std::string rrv_name = rrv->GetName();
        if (rrv_name != name) continue;
        if (val_lo != 0.0) {
            rrv->setAsymError(val_lo,val_hi);
        } else {
            rrv->setError(val_hi);
        }
    }
}

// Find a specific RooRealVar from a RooArgList
double getRRV(RooArgList lst, std::string name) {
    RooLinkedListIter iterP = lst.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        std::string rrv_name = rrv->GetName();
        if (rrv_name == name) {
            return rrv->getVal();
        }
    }
    return -1;
}

// Iterates over the first set and removes errors from ones which appear in the second set
void removeErrors(RooArgSet pars,RooArgSet pois) {
    RooLinkedListIter it1 = pars.iterator();
    for (RooRealVar* rrv = (RooRealVar*) it1.Next(); rrv != 0; rrv = (RooRealVar*) it1.Next()) {
        std::string n1 = rrv->GetName();
        RooLinkedListIter it2 = pois.iterator();
        for (RooRealVar* poi = (RooRealVar*) it2.Next(); poi !=0; poi = (RooRealVar*) it2.Next()) {
            std::string n2 = poi->GetName();
            if (n1 == n2) {            
                rrv->removeAsymError();
                rrv->removeError();
                break;
            }        
        }
    }
}

// Returns the mapping of ch <-> long string from a text datacard
std::map<std::string,TString> get_channel_map(TString fpath, bool reverse=false) {
    std::map<std::string,TString> ch_map;
    ifstream inf(fpath);
    if (!inf) {
        std::cout << "[ERROR] Unable to open file: " << fpath << std::endl;
        return ch_map;
    }

    std::cout << "Parsing: " << fpath << std::endl;

    uint CH_IDX(2);
    uint NAME_IDX(3);

    std::string line;

    /* Eat the header information */
    while (!inf.eof()) {
        std::getline(inf,line);
        TString t_line(line);
        if (t_line.BeginsWith("---")) {
            break;
        }
    }

    /* Parse the ch <-> name mapping */
    while (!inf.eof()) {
        std::getline(inf,line);
        TString t_line(line);
        if (t_line.BeginsWith("---")) {
            break;
        }

        std::vector<std::string> split;
        split_string(line,split);

        /* Remove all blank spaces from the vector */
        for (auto it = split.begin(); it != split.end();) {
            TString t_line(*it);
            if (t_line.EqualTo("")) {
                it = split.erase(it);
            } else {
                it++;
            }
        }
        TString ch = split.at(CH_IDX);
        TString name = split.at(NAME_IDX);
        
        name = name.ReplaceAll("ttx_multileptons-","").ReplaceAll(".root","");

        if (reverse) {
            ch_map[name.Data()] = ch;
        } else {
            ch_map[ch.Data()] = name;
        }
    }

    return ch_map;
}
