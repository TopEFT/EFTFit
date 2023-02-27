#ifndef PLOTGROUP_H_
#define PLOTGROUP_H_

#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <unordered_map>
#include <utility>
#include <stdio.h>
#include <dirent.h>

#include "TString.h"

#include "PlotData.h"

typedef std::vector<TString> vTStr;

std::unordered_map<std::string,std::string> BIN_LABEL_MAP {
    // For use with eps and ps save types
    {"2lss_m","2\\ell\\text{ss 2b} (-)"},
    {"2lss_p","2\\ell\\text{ss 2b} (+)"},
    {"2lss_4t_m","2\\ell\\text{ss 3b} (-)"},
    {"2lss_4t_p","2\\ell\\text{ss 3b} (+)"},
    {"3l_p_offZ_1b","3\\ell \\text{ off-Z 1b}(+)"},
    {"3l_m_offZ_1b","3\\ell \\text{ off-Z 1b}(-)"},
    {"3l_p_offZ_2b","3\\ell \\text{ off-Z 2b}(+)"},
    {"3l_m_offZ_2b","3\\ell \\text{ off-Z 2b}(-)"},
    {"3l_onZ_1b","3\\ell \\text{ on-Z 1b}"},
    {"3l_onZ_2b","3\\ell \\text{ on-Z 2b}"},
    {"4l","4\\ell"},
    {"3l_onZ_2b_2j3j","3\\ell \\text{ on-Z 2b 2j3j}"},
    {"3l_onZ_2b_4j5j","3\\ell \\text{ on-Z 2b 4j5j}"},

    {"2lss_p_4j"     ,"4"},
    {"2lss_p_5j"     ,"5"},
    {"2lss_p_6j"     ,"6"},
    {"2lss_p_7j"     ,"7"},

    {"2lss_m_4j"     ,"4"},
    {"2lss_m_5j"     ,"5"},
    {"2lss_m_6j"     ,"6"},
    {"2lss_m_7j"     ,"7"},
    
    {"2lss_4t_p_4j"  ,"4"},
    {"2lss_4t_p_5j"  ,"5"},
    {"2lss_4t_p_6j"  ,"6"},
    {"2lss_4t_p_7j"  ,"7"},

    {"2lss_4t_m_4j"  ,"4"},
    {"2lss_4t_m_5j"  ,"5"},
    {"2lss_4t_m_6j"  ,"6"},
    {"2lss_4t_m_7j"  ,"7"},

    {"3l_p_offZ_1b_2j"  ,"2"},
    {"3l_p_offZ_1b_3j"  ,"3"},
    {"3l_p_offZ_1b_4j"  ,"4"},
    {"3l_p_offZ_1b_5j"  ,"5"},

    {"3l_m_offZ_1b_2j"  ,"2"},
    {"3l_m_offZ_1b_3j"  ,"3"},
    {"3l_m_offZ_1b_4j"  ,"4"},
    {"3l_m_offZ_1b_5j"  ,"5"},

    {"3l_p_offZ_2b_2j"  ,"2"},
    {"3l_p_offZ_2b_3j"  ,"3"},
    {"3l_p_offZ_2b_4j"  ,"4"},
    {"3l_p_offZ_2b_5j"  ,"5"},

    {"3l_m_offZ_2b_2j"  ,"2"},
    {"3l_m_offZ_2b_3j"  ,"3"},
    {"3l_m_offZ_2b_4j"  ,"4"},
    {"3l_m_offZ_2b_5j"  ,"5"},

    {"3l_onZ_1b_2j"     ,"2"},
    {"3l_onZ_1b_3j"     ,"3"},
    {"3l_onZ_1b_4j"     ,"4"},
    {"3l_onZ_1b_5j"     ,"5"},

    {"3l_onZ_2b_2j"     ,"2"},
    {"3l_onZ_2b_3j"     ,"3"},
    {"3l_onZ_2b_4j"     ,"4"},
    {"3l_onZ_2b_5j"     ,"5"},

    {"4l_2j"         ,"2"},
    {"4l_3j"         ,"3"},
    {"4l_4j"         ,"4"},
};

std::unordered_map<std::string,std::string> BIN_LABEL_MAP_DIVIDED {
    // Inserted a line breaker into the 3l onZ 2b categories
    {"2lss_m","2\\ell\\text{ss 2b} (-)"},
    {"2lss_p","2\\ell\\text{ss 2b} (+)"},
    {"2lss_4t_m","2\\ell\\text{ss 3b} (-)"},
    {"2lss_4t_p","2\\ell\\text{ss 3b} (+)"},
    {"3l_p_offZ_1b","3\\ell \\text{ off-Z 1b}(+)"},
    {"3l_m_offZ_1b","3\\ell \\text{ off-Z 1b}(-)"},
    {"3l_p_offZ_2b","3\\ell \\text{ off-Z 2b}(+)"},
    {"3l_m_offZ_2b","3\\ell \\text{ off-Z 2b}(-)"},
    {"3l_onZ_1b","3\\ell \\text{ on-Z 1b}"},
    {"3l_onZ_2b","3\\ell \\text{ on-Z 2b}"},
    {"4l","4\\ell"},
    {"3l_onZ_2b_2j3j","\\splitline{3\\ell \\text{ on-Z}}{\\text{2b 2j3j}}"},
    {"3l_onZ_2b_4j5j","\\splitline{3\\ell \\text{ on-Z}}{\\text{2b 4j5j}}"},
};

struct PlotGroup {
    std::vector<std::string> gname;
    std::vector<int> gbins;
    std::vector<std::string> gtxt1;
    std::vector<std::string> gtxt2;
    //std::vector<TLatex> glatex;
    PlotGroup() {
        gname  = {};
        gbins  = {};  // num of bins of each division
        gtxt1  = {};  // for the SRs
        gtxt2  = {};  // for the njet cats
    }
};

PlotGroup autoPartition(PlotData pData, std::map<std::string,TString> ch_map = {}) {
    PlotGroup pGroup;
    PlotData pData_agg = aggregateDifferential(pData);
    int offset=0;
    for (int i=0; i<pData_agg.SR_name.size(); i++) {
        pGroup.gname.push_back(pData_agg.SR_name[i].Data());
        if (!(ch_map.empty())) {
            for (const auto & [lstring, ch] : ch_map) {
                if (pData_agg.SR_name[i] == ch) {
                    pGroup.gtxt2.push_back(BIN_LABEL_MAP[lstring]);
                }
            }
        }
        else pGroup.gtxt1.push_back(BIN_LABEL_MAP[pData_agg.SR_name[i].Data()]);
        for (int j=1; j+offset<=pData.SR_name.size(); j++) {
            if ((pData.SR_name[j+offset] != pData_agg.SR_name[i]) | (j+offset == pData.SR_name.size())) {  // The second condition is for preventing it hitting the end of PlotData.
                pGroup.gbins.push_back(j);
                offset += j;
                break;  // stop incrementing when reaching the next channel
            }
        }
    }
    return pGroup;
}

PlotGroup SRPartition(PlotData pData) {
    PlotGroup pGroup;
    for (int i=0; i<SR_list.size(); i++) {
        pGroup.gname.push_back(SR_list[i].Data());
        pGroup.gbins.push_back(cat_groups[SR_list[i].Data()].size());  // use the length of the channel vectors as the num of bins
        pGroup.gtxt1.push_back(BIN_LABEL_MAP[SR_list[i].Data()]);
    }
    return pGroup;
}

PlotGroup SRRepartition(PlotData pData, PlotGroup pGroup, vTStr refSR = SR_list_2) {
     PlotGroup pGroup_repart;
     int offset = 0;
     for (int i=0; i<refSR.size(); i++) {
        pGroup_repart.gname.push_back(refSR[i].Data());
        pGroup_repart.gtxt1.push_back(BIN_LABEL_MAP_DIVIDED[refSR[i].Data()]);
        
        int nchs = cat_groups[refSR[i].Data()].size();
        int nbs  = 0;
        int idx  = 0;
        for (idx=0; idx<nchs; idx++) {
             nbs += pGroup.gbins[idx + offset];
        }
        pGroup_repart.gbins.push_back(nbs);
        offset += idx;
    }
    return pGroup_repart;
}

void print_PlotGroup(PlotGroup pGroup) {
    for (std::string part: pGroup.gname) {
        cout << part << ' ';
    }
    for (int gbin: pGroup.gbins) {
        cout << gbin << ' ';
    }
    if (pGroup.gtxt1.size()) {
        cout << "txt1: " << endl;
        for (std::string t1: pGroup.gtxt1) {
            cout << t1 << ' ';
        }
    }
    if (pGroup.gtxt2.size()) {
        cout << "txt2: " << endl;
        for (std::string t2: pGroup.gtxt2) {
            cout << t2 << ' ';
        }
    }
}

#endif
/* PLOTGROUP_H_ */