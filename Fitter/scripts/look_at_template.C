// March 14, 2022
// Some notes about this script:
//    - Opens a root file that should contain template histos created by topcoffea's datacard_maker.py
//    - Prints the values of the nominal and up/down histos at a given theta (theta>=1)
//    - The format it prints the info should look like a python dictionary (for easy pasting into a py script)
//      but note it would of course be better to dump directly into e.g. a json
//    - If theta>1, performs a linear extrapolation that should match what combine does see combine documentation
//      https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part2/settinguptheanalysis/
//    - Also can dump the plots into some png files if you uncomment that part
//    - Note this script is really basic and there are a lot of ways it could be improved to be more usable 
//
// To run the script:
// root -l -b -q look_at_template.C


// Check if a sub string is present in a string
bool has_substr(TString s, TString substr){
    return (s.Index(substr) != -1);
}

// Print contents of the hist
void print_hist_contents(TH1D* h_in,TString tag="Histo") {
    for (Int_t bin_idx = 1; bin_idx <= h_in->GetNbinsX(); bin_idx++) {
        double bin_val = h_in->GetBinContent(bin_idx);
        double bin_num = h_in->GetBinLowEdge(bin_idx);
        std::cout << "    \"" << tag <<  "_" << bin_num << "\"" << " : " << bin_val << "," << std::endl;
    }
}

// Shift a hist by a linear theta thift
void shift_hist_by_theta(const TH1D* h_n, TH1D* h_v, double theta) {
    for (Int_t bin_idx = 1; bin_idx <= h_n->GetNbinsX(); bin_idx++) {
        double bin_val_n = h_n->GetBinContent(bin_idx);
        double bin_val_v = h_v->GetBinContent(bin_idx);
        double delta = bin_val_v - bin_val_n;
        double bin_val_shifted = bin_val_n + delta*abs(theta);
        h_v->SetBinContent(bin_idx,bin_val_shifted);
    }
}


// Main function
void look_at_template(){

    // The theta value to look at for up and down hists (if we are going to do the extrapolation)
    bool extrap_theta = true;
    double theta_abs = 1.0; // Note this should always be positive, and must be >=1 (not set up to do the interpolation, only extrapolation)

    // Whether or not to also dump the histos into png files
    bool make_plots = false;

    // Open the file (could do this in a better way, e.g. pass as an argument, also probably should loop over templates)
    TString file_path =  "path/to/your/templates"; // Path to dir with template histos
    TString file_name =  "ttx_multileptons-2lss_4t_m_2b.root";
    //TString file_name =  "ttx_multileptons-2lss_4t_p_2b.root";
    //TString file_name =  "ttx_multileptons-2lss_m_2b.root";
    //TString file_name =  "ttx_multileptons-2lss_p_2b.root";
    //TString file_name =  "ttx_multileptons-3l1b_m.root";
    //TString file_name =  "ttx_multileptons-3l1b_p.root";
    //TString file_name =  "ttx_multileptons-3l2b_m.root";
    //TString file_name =  "ttx_multileptons-3l2b_p.root";
    //TString file_name =  "ttx_multileptons-3l_sfz_1b.root";
    //TString file_name =  "ttx_multileptons-3l_sfz_2b.root";
    //TString file_name =  "ttx_multileptons-4l_2b.root";
    TFile* file = TFile::Open(file_path+file_name);
    std::cout << "\nLooking at histos in: " << file_path+file_name << std::endl;

    // We're printing the info in a form that we can paste into a py file as a py dictionary (would be better to write it to a file instead of just printing)
    std::cout << "template_vals_dict = {" << std::endl;

    // Loop over the histos in the file
    for (auto&& keyAsObj : *file->GetListOfKeys()){

        // Get the name
        auto key = (TKey*) keyAsObj;
        TString s = key->GetName();

        // Skip the data histo as we don't care about it for this
        if (has_substr(s,"data")) { continue; }
        // Skip the up and down variations (we will call those directly)
        if (has_substr(s,"Up") or has_substr(s,"Down")){ continue; }

        // Get nom up and down hists
        TH1D* h_n = (TH1D*)file->Get(s);
        TH1D* h_u = (TH1D*)file->Get(s+"_renormfactUp");
        TH1D* h_d = (TH1D*)file->Get(s+"_renormfactDown");

        // If you just want to dump the raw numbers, this block is all you need (and can can skip rest of script)
        //std::cout << "BEFORE" << std::endl;
        //print_hist_contents(h_n,s);
        //print_hist_contents(h_u,s+"_renormfactUp");
        //print_hist_contents(h_d,s+"_renormfactDown");
        //continue;

        // If we want to do the extrapolation of theta (probably this should go in a separate function)
        if (extrap_theta) {
            // Unit normalize
            double A_n = h_n->Integral();
            double A_u = h_u->Integral();
            double A_d = h_d->Integral();
            h_n->Scale(1.0/A_n);
            h_u->Scale(1.0/A_u);
            h_d->Scale(1.0/A_d);

            // Shift up and down by theta
            shift_hist_by_theta(h_n,h_u,theta_abs);
            shift_hist_by_theta(h_n,h_d,theta_abs);

            // Scale the hist back to account for normalization
            double kappa_u = A_u/A_n;
            double kappa_d = A_n/A_d;
            double norm_factor_u = A_n*pow(kappa_u,theta_abs);
            double norm_factor_d = A_n*pow(kappa_d,-theta_abs);
            h_n->Scale(A_n);
            h_u->Scale(norm_factor_u);
            h_d->Scale(norm_factor_d);

            // Here are the numbers after extrapolating theta
            //std::cout << "AFTER SCALE" << std::endl;
            print_hist_contents(h_n,s);
            print_hist_contents(h_u,s+"_renormfactUp");
            print_hist_contents(h_d,s+"_renormfactDown");
        }


        // Can also make some plots if you want (probably should go in a separate function)
        if (make_plots) {

            // Make plots etc
            cout << "\n" << s << " " << key->GetClassName() << endl;

            // Keep track of max bin val, and print out bin vals
            float max_binval = 0;
            for (Int_t bin_idx = 0; bin_idx <= h_n->GetNbinsX()+1; bin_idx++) {
                float v_n = h_n->GetBinContent(bin_idx);
                if (v_n > max_binval) { max_binval = v_n; }
                std::cout << "\tBin " << bin_idx << " (low edge: " << h_n->GetBinLowEdge(bin_idx) << ") " << ": " << v_n << std::endl; // Print some info
            }
            for (Int_t bin_idx = 0; bin_idx <= h_u->GetNbinsX()+1; bin_idx++) {
                float v_n = h_u->GetBinContent(bin_idx);
                if (v_n > max_binval) { max_binval = v_n; }
            }
            for (Int_t bin_idx = 0; bin_idx <= h_d->GetNbinsX()+1; bin_idx++) {
                float v_n = h_d->GetBinContent(bin_idx);
                if (v_n > max_binval) { max_binval = v_n; }
            }

            // Draw
            TCanvas *c1 = new TCanvas("c1","",500,500);
            h_u->Draw("E");
            h_n->Draw("E SAME");
            h_d->Draw("E SAME");

            // Set the colors
            h_u->SetLineColor(3);
            h_n->SetLineColor(1);
            h_d->SetLineColor(4);

            h_u->GetYaxis()->SetRangeUser(0,max_binval*1.2);

            c1->Print(s+".png","png");
            delete c1;
        }

    }

    // For the py dictionary that we are printing...
    std::cout << "}" << std::endl;


}
