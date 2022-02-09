#ifndef ANALYSISCATEGORY_H_
#define ANALYSISCATEGORY_H_

#include <set>

#include "TString.h"

#include "RooWorkspace.h"
#include "RooFitResult.h"
#include "RooAbsData.h"
#include "RooDataSet.h"
#include "RooCatType.h"
#include "RooAddition.h"

#include "WSHelper.h"

// >VERY< useful convenience class for extracting expected and observed yields of some category from
// a given RooWorkspace.
//  * Has methods for creating new categories that are the merger of other categories from the RooWorkspace
//  * The class stores ptrs to the actual RooObjects located in the RooWorkspace, so changing parameters
//    (e.g. POIs/Nuis Parameters) will be reflected in the objects stored in this class automatically.
//  * N.B.: For the methods which return the expected error in a category, the correlations needed for
//    the error calculation come from a RooFitResult object passed to those methods, which has objects
//    that are separate from the ones found in the RooWorkspace. As a result, modifying values in certain
//    objects from the RooWorkspace (e.g. nuisance parameters' Hi/Lo errors) won't be reflected in the result
//    returned by the methods that make use of a RooFitResult object, such as getExpProcError()
class AnalysisCategory {
    public:
        Int_t proc_width;
        TString cat_name;
        RooDataSet* roo_data;
        RooDataSet* asimov_data;
        bool use_asimov;
        std::unordered_map<std::string,RooAddition*> exp_proc;  // The RooAddition objects contain the
                                                                //  expected yield for a specific process

        std::vector<TString> proc_order;    // Maintains a consistent ordering of the processes
        std::vector<TString> children;      // Contains the names of the categories merged into this one

        WSHelper helper;    // Kind of annoying that we have to initialize one helper per Category...

        AnalysisCategory(TString category, RooWorkspace* ws);
        AnalysisCategory(TString category, std::vector<AnalysisCategory> others);
        AnalysisCategory(TString category, std::vector<AnalysisCategory*> others);
        ~AnalysisCategory();

        void mergeInit(TString category, std::vector<AnalysisCategory> others);

        bool hasProc(TString proc);
        TString getName();
        std::vector<TString> getProcs();
        std::vector<TString> getChildren();
        RooDataSet* getRooData();
        RooAddition* getRooAdd(TString proc);
        double getData();
        double getExpProc(TString proc);
        double getExpProcError(TString, RooFitResult* fr=0);
        double getExpSum();
        double getExpSumError(RooFitResult* fr=0);
        void setProcOrder(std::vector<TString> order);
        void mergeProcesses(TRegexp rgx,TString new_name);
        void Print(RooFitResult* fr=0);
        void setAsimov();
};

// Normal constructor
AnalysisCategory::AnalysisCategory(TString category, RooWorkspace* ws) {
    this->cat_name = category;
    this->helper = WSHelper();

    std::vector<RooCatType*> all_cats = this->helper.getTypes(ws,"CMS_channel");
    std::vector<RooCatType*> tar_cats = this->helper.filter(all_cats,category);
    std::vector<RooAbsData*> obs_data = this->helper.getObsData(ws,"data_obs","CMS_channel",tar_cats);
    if (obs_data.size() != 1) {
        std::cout << TString::Format("[WARNING] obs_data incorrect size: %zu",obs_data.size()) << std::endl;
        throw;
    }
    this->roo_data = (RooDataSet*)obs_data.at(0);
    this->asimov_data = (RooDataSet*)obs_data.at(0);
    this->use_asimov = false;   // Determine if getData() function return asimov data or real data
    std::vector<RooAbsReal*> exp_cat = this->helper.getExpCatFuncs(ws,tar_cats);

    TString search("_proc_");
    this->proc_width = 0;
    for (RooAddition* ra: this->helper.toRooAdd(exp_cat)) {
        TString name(ra->GetName());
        Ssiz_t idx(name.Index(search));
        if (idx == TString::kNPOS) {
            std::cout << TString::Format("[WARNING] Unable to find %s in %s",search.Data(),name.Data()) << std::endl;
            throw;
        }
        name = name(idx+search.Length(),name.Length());
        this->exp_proc[name.Data()] = ra;
        this->proc_order.push_back(name);
        this->proc_width = std::max(this->proc_width,name.Length());
    }
}

// Construct an AnalysisCategory by merging together everything from 'others'
AnalysisCategory::AnalysisCategory(TString category, std::vector<AnalysisCategory> others) {
    this->mergeInit(category,others);
}

// Overloaded constructor for vectors of ptrs
// NOTE: I don't know if overloading the ctor like this is taboo or not, just make note
//  of the fact that if we tried to flip the order of the ctor delegation by using a
//  'mergeInit()' method that takes a vector of ptrs instead, it all fails horribly!
AnalysisCategory::AnalysisCategory(TString category, std::vector<AnalysisCategory*> others) {
    std::vector<AnalysisCategory> vec;
    for (AnalysisCategory* a: others) {
        vec.push_back(*a);
    }
    this->mergeInit(category,vec);
}

AnalysisCategory::~AnalysisCategory() {}

// Define a common initilizer method for overloading the ctors used for merging categories
void AnalysisCategory::mergeInit(TString category, std::vector<AnalysisCategory> others) {
    this->cat_name = category;
    this->helper = WSHelper();
    this->proc_width = 0;
    this->roo_data = nullptr;   // Temporarily set to a nullptr
    // First find all unique processes among the AnalysisCategories to be merged, also merge
    //  the RooDataSets together at this time
    for (auto ana_cat: others) {
        this->children.push_back(ana_cat.getName());
        RooDataSet* other_data = ana_cat.getRooData();
        // NOTE: RooDataSet::merge() does not do what I thought it does, so have to 'merge' the
        //  datasets using RooDataSet::append() instead
        if (!this->roo_data) {
            this->roo_data = (RooDataSet*)other_data->Clone(category);
        } else {
            this->roo_data->append(*other_data);
        }
        RooDataSet* other_asimov_data = ana_cat.asimov_data;
        if (!this->asimov_data) {
            this->asimov_data = (RooDataSet*)other_asimov_data->Clone(category);
        } else {
            this->asimov_data->append(*other_asimov_data);
        }
        for (TString p: ana_cat.getProcs()) {
            if (!this->hasProc(p)) {
                this->exp_proc[p.Data()] = nullptr;  // Temporarily set to a nullptr
                this->proc_order.push_back(p);
                this->proc_width = std::max(this->proc_width,p.Length());
            }
        }
    }
    // Next iterate over all processes collecting the RooAddition object from each category and merge
    //  it with the rest
    for (TString p: this->getProcs()) {
        std::vector<RooAddition*> to_merge;
        TString merge_name = TString("n_exp_bin") + category + TString("_proc_") + p;
        for (auto ana_cat: others) {
            if (!ana_cat.hasProc(p)) continue;
            to_merge.push_back(ana_cat.getRooAdd(p));
        }
        RooAddition* roo_merged = this->helper.merge(to_merge,merge_name);
        this->exp_proc[p.Data()] = roo_merged;
    }
}

// Check if the specfied process exists in this category
bool AnalysisCategory::hasProc(TString proc) {
    std::string s(proc.Data());
    return this->exp_proc.count(s);
}

TString AnalysisCategory::getName() {
    return this->cat_name;
}

std::vector<TString> AnalysisCategory::getProcs() {
    return this->proc_order;
}

std::vector<TString> AnalysisCategory::getChildren() {
    return this->children;
}

// Returns a ptr to the actual RooDataSet object for this category
RooDataSet* AnalysisCategory::getRooData() {
    return this->roo_data;
}

// Returns a ptr to the RooAddition object for a particular process
RooAddition* AnalysisCategory::getRooAdd(TString proc) {
    std::string s(proc.Data());
    if (!this->hasProc(proc)) {
        throw;
    }
    return this->exp_proc[s];
}

// Returns the number of events in this category (which may be a merged category)
double AnalysisCategory::getData() {
    if (this->use_asimov) {
        return this->asimov_data->sumEntries();
    }
    else {
        if (this->roo_data) {
            return this->roo_data->sumEntries();
        }
        else {
            return 0.0;
        }
    }
    return this->roo_data->sumEntries();
}

// Return the expected yield for a specific process
double AnalysisCategory::getExpProc(TString proc) {
    if (this->hasProc(proc)) {
        return this->getRooAdd(proc)->getVal();
    }
    return 0.0;
}

// Return the propagated error for a specific process
double AnalysisCategory::getExpProcError(TString proc, RooFitResult* fr) {
    if (this->hasProc(proc) && fr) {
        RooAddition* roo_add = this->getRooAdd(proc);
        return roo_add->getPropagatedError(*fr);
    }
    return 0.0;
}

// Return the expected yield summed over all processes
double AnalysisCategory::getExpSum() {
    double sum(0.0);
    for (TString p: this->getProcs()) {
        sum += this->getExpProc(p);
    }
    return sum;
}

double AnalysisCategory::getExpSumError(RooFitResult* fr) {
    if (!fr) {
        return 0.0;
    }
    TString s("tmp_merged");
    std::vector<RooAddition*> to_merge;
    for (TString p: this->getProcs()) {
        to_merge.push_back(this->getRooAdd(p));
    }
    RooAddition* tmp_mrg = this->helper.merge(to_merge,s);
    double err = tmp_mrg->getPropagatedError(*fr);
    // I don't know if this is a good idea or not...
    delete tmp_mrg;

    return err;
}

void AnalysisCategory::setProcOrder(std::vector<TString> order) {
    std::vector<TString> new_order;
    std::set<TString> tmp_set;
    for (TString s: order) {
        // Only sets the order for processes contained in this AnaCat
        if (this->hasProc(s)) {
            new_order.push_back(s);
            tmp_set.insert(s);
        }
    }

    // Add in any processes that weren't specified by the order vector
    for (TString s: this->getProcs()) {
        if (tmp_set.count(s)) {
            continue;
        }
        new_order.push_back(s);
    }
    this->proc_order = new_order;

    // std::cout << "New Process Order:" << std::endl;
    // for (TString s: this->getProcs()) {
    //     std::cout << "\t" << s << std::endl;
    // }
}

// Merges together any processes that match 'rgx' and takes care to update
//  the 'proc_width' and 'proc_order' data members to reflect mergers
void AnalysisCategory::mergeProcesses(TRegexp rgx, TString new_name) {
    std::vector<RooAddition*> procs_to_merge;
    std::vector<TString> new_order; // We need to overwrite proc_order with only the objects that we are going to keep
    this->proc_width = 0;   // Reset the width measure
    for (TString name: this->getProcs()) {
        RooAddition* ra = this->getRooAdd(name);
        Ssiz_t len = name.Length();
        bool chk = (rgx.Index(name,&len) > -1);
        if (chk) {
            procs_to_merge.push_back(ra);
            this->exp_proc.erase(name.Data());  // Remove any procs that we're going to merge together
        } else {
            new_order.push_back(name);
            this->proc_width = std::max(this->proc_width,name.Length());
        }
    }
    new_order.push_back(new_name);
    this->proc_width = std::max(this->proc_width,new_name.Length());

    RooAddition* merged_process = this->helper.merge(procs_to_merge,new_name);
    this->exp_proc[new_name.Data()] = merged_process;
    this->proc_order = new_order;
} 

void AnalysisCategory::Print(RooFitResult* fr) {
    int pwidth = std::max(5,this->proc_width);
    int dwidth = 5; // Digit width
    TString line_break = TString(' ',pwidth - dwidth) + TString('-',1+2*dwidth);
    double val,err;
    TString frmt;

    std::cout << "Category: " << this->getName() << std::endl;
    std::cout << TString::Format("%*s: %*.1f",pwidth,"data",dwidth,this->getData()) << std::endl;
    for (TString p: this->getProcs()) {
        val = this->getExpProc(p);
        if (fr) {
            err = this->getExpProcError(p,fr);
        } else {
            err = 0.0;
        }
        frmt = TString::Format("%*.1f +/- %.1f",dwidth,val,err);
        std::cout << TString::Format("%*s: %s",pwidth,p.Data(),frmt.Data()) << std::endl;
    }
    std::cout << line_break << std::endl;
    val = this->getExpSum();
    if (fr) {
        err = this->getExpSumError(fr);
    } else {
        err = 0.0;
    }
    frmt = TString::Format("%*.1f +/- %.1f",dwidth,val,err);
    std::cout << TString::Format("%*s: %s",pwidth,"Sum",frmt.Data()) << std::endl;

    // for (TString p: this->getProcs()) {
    //     RooAddition* r = this->getRooAdd(p);
    //     r->Print();
    // }
    // std::cout << std::endl;
    // this->roo_data->Print();
    // this->roo_data->printArgs(std::cout);
    // this->roo_data->printMultiline(std::cout,1);
}

void AnalysisCategory::setAsimov() {
    this->use_asimov = true;
    RooCategory roo_cat("asimov","asimov");
    roo_cat.defineType("asimov");
    RooRealVar rrv("_weight_","_weight_",0);
    RooDataSet* rds = new RooDataSet("asimov_data","asimov_data",RooArgSet(rrv,roo_cat),"_weight_");
    rds->add(roo_cat, this->getExpSum());
    this->asimov_data = rds;
}

#endif
/* ANALYSISCATEGORY */
