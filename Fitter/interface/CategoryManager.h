#ifndef CATEGORYMANAGER_H_
#define CATEGORYMANAGER_H_

#include <string>
#include <vector>
#include <unordered_map>

#include "TString.h"

#include "RooWorkspace.h"
#include "RooCatType.h"

#include "AnalysisCategory.h"
#include "WSHelper.h"

// Wrapper class to manage a collection of AnalysisCategory objects

class CategoryManager {
    public:
        // std::vector<TString> proc_order;

        // NOTE: second part of the map needs to be a ptr, otherwise the map ctor fails horribly (for some unknown reason)!
        std::unordered_map<std::string,AnalysisCategory*> all_cats;

        // Note: This currently isn't used anywhere and duplicates information already contained in the above map
        std::vector<TString> cat_names;

        CategoryManager(RooWorkspace* ws, WSHelper ws_helper,std::vector<TString> proc_order);
        ~CategoryManager();

        bool hasCategory(TString name);
        AnalysisCategory* getCategory(TString name);
        std::vector<AnalysisCategory*> getCategories(std::vector<TString> names);
        std::vector<AnalysisCategory*> getChildCategories(TString name);
        std::vector<AnalysisCategory*> getChildCategories(std::vector<TString> names);

        void mergeProcesses(TRegexp rgx, TString new_name);
        void mergeCategories(TString mrg_name, std::vector<TString> cat_names, std::vector<TString> proc_order);
        void renameCategory(TString old_name, TString new_names);

};

// Normal constructor
CategoryManager::CategoryManager(RooWorkspace* ws, WSHelper ws_helper, std::vector<TString> proc_order) {
    for (RooCatType* c: ws_helper.getTypes(ws)) {
        TString cat_name(c->GetName());
        AnalysisCategory* ana_cat = new AnalysisCategory(c->GetName(),ws);
        ana_cat->setProcOrder(proc_order);
        this->all_cats[cat_name.Data()] = ana_cat;
        this->cat_names.push_back(cat_name);
    }
}

// Default destructor
CategoryManager::~CategoryManager() {}

bool CategoryManager::hasCategory(TString name) {
    return this->all_cats.count(name.Data());
}

// Returns a specific category
AnalysisCategory* CategoryManager::getCategory(TString name) {
    return this->all_cats[name.Data()];
}

// Returns a vector of categories
std::vector<AnalysisCategory*> CategoryManager::getCategories(std::vector<TString> names) {
    std::vector<AnalysisCategory*> cats;
    for (TString name: names) {
        cats.push_back(this->getCategory(name));
    }
    return cats;
}

// Returns a vector of categories that were merged into 'name'
// Note: Only 'merged' categories will have children!
std::vector<AnalysisCategory*> CategoryManager::getChildCategories(TString name) {
    std::vector<AnalysisCategory*> children;
    if (!this->hasCategory(name)) {
        std::cout << TString::Format("[WARNING] getChildCategories(): Unknown category - %s",name.Data()) << std::endl;
        return children;
    }
    AnalysisCategory* parent = this->getCategory(name);
    std::vector<TString> children_names = parent->getChildren();
    for (TString s: children_names) {
        if (!this->hasCategory(s)) {
            std::cout << TString::Format("[WARNING] getChildCategories(): Unknown child - %s",s.Data()) << std::endl;
            continue;
        }
        AnalysisCategory* child = this->getCategory(s);
        children.push_back(child);
    }
    return children;
}

// Overloaded method for returning all the child categories from multiple merged categories
std::vector<AnalysisCategory*> CategoryManager::getChildCategories(std::vector<TString> names) {
    std::vector<AnalysisCategory*> children;
    for (TString name: names) {    
        for (AnalysisCategory* child: this->getChildCategories(name)) {
            children.push_back(child);
        }
    }
    return children;
}

// Calls the `mergeProcesses` method on each AnalysisCategory owned by the manager
void CategoryManager::mergeProcesses(TRegexp rgx, TString new_name) {
    for (TString name: this->cat_names) {
        AnalysisCategory* ana_cat = this->getCategory(name);
        ana_cat->mergeProcesses(rgx,new_name);
    }
}

/*
Desc:
    Create some merged categories, i.e. create a new category which is the merger of all sub-categories
    of the ones specified in 'cat_names'. The new merged category will have its name specified by 'mrg_name'
*/
void CategoryManager::mergeCategories(TString mrg_name, std::vector<TString> cat_names, std::vector<TString> proc_order) {
    std::vector<AnalysisCategory*> to_merge;
    
    if (this->hasCategory(mrg_name)) {
        // Invalid mrg_name
        std::cout << TString::Format("[WARNING] Unable to merge categories. Invalid merge name: %s",mrg_name.Data()) << std::endl;
        return;
    }
    for (TString s: cat_names) {
        if (!this->hasCategory(s)) {
            std::cout << TString::Format("[WARNING] Skipping unknown category: %s",s.Data()) << std::endl;
            continue;
        }
        AnalysisCategory* cat = this->getCategory(s);
        to_merge.push_back(cat);
    }
    
    for (AnalysisCategory* cat_merge: to_merge) {
        cat_merge->setAsimov();
    }
    
    AnalysisCategory* merged_cat = new AnalysisCategory(mrg_name,to_merge);
    merged_cat->setProcOrder(proc_order);
    this->all_cats[mrg_name.Data()] = merged_cat; // This might be a bit spicy...
    this->cat_names.push_back(mrg_name);
}


void CategoryManager::renameCategory(TString new_name, TString old_name) {
    if (this->hasCategory(new_name)) {
        // Invalid new_name
        std::cout << TString::Format("[WARNING] Unable to rename category. Category already exists: %s",new_name.Data()) << std::endl;
        return;
    }
    if (!this->hasCategory(old_name)) {
        std::cout << TString::Format("[WARNING] Unable to find category: %s",old_name.Data()) << std::endl;
        return;
    }
    AnalysisCategory* cat = this->getCategory(old_name.Data());
    cat->cat_name = new_name.Data();
    this->all_cats[new_name.Data()] = cat;
}

#endif
/* CATEGORYMANAGER */
