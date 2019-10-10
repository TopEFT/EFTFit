#include <vector>
#include <list>

#include "TString.h"

#include "RooArgSet.h"
#include "RooLinkedListIter.h"
#include "RooRealVar.h"
#include "RooAbsData.h"

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

// Sets the value of the RooRealVar based on 'type'
void set_rrv(RooRealVar* rrv, TString type, double sigma) {
    rrv->removeRange();
    double nom_var  = rrv->getVal();
    double down_var = rrv->getVal() + rrv->getErrorLo()*sigma;
    double up_var   = rrv->getVal() + rrv->getErrorHi()*sigma;
    if (type == "up") {
        // Sets the rrv to the up fluct*sigma
        rrv->setVal(up_var);
    } else if (type == "down") {
        // Sets the rrv to the down fluct*sigma
        rrv->setVal(down_var);
    } else if (type == "nom") {
        // Sets the rrv to a specific value
        rrv->setVal(sigma);
    }
}

void set_rrv(TString name, RooArgSet& arg_set, TString type, double sigma) {
    RooRealVar* rrv = (RooRealVar*)arg_set.find(name);
    if (!rrv) {
        std::cout << "Unknown RRV: " << name << std::endl;
        return;
    }
    set_rrv(rrv,type,sigma);
}

void print_rrv(RooRealVar* rrv, RooFitResult& fr) {
    std::cout << "RRV " << rrv->GetName() << ":"
              << "\n  Val: "     << rrv->getVal()
              << "\n  Err: "     << rrv->getError()
              << "\n  Lo:  "     << rrv->getErrorLo()
              << "\n  Hi:  "     << rrv->getErrorHi()
              << "\n  AsymLo: "  << rrv->getAsymErrorLo()
              << "\n  AsymHi: "  << rrv->getAsymErrorHi()
              << "\n  PropErr: " << rrv->getPropagatedError(fr)
              << std::endl;
}

void print_rrv(TString name, RooArgSet& arg_set, RooFitResult& fr) {
    RooRealVar* rrv = (RooRealVar*)arg_set.find(name);
    if (!rrv) {
        std::cout << "Unknown RRV: " << name << std::endl;
        return;
    }
    print_rrv(rrv,fr);

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