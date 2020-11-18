import ROOT

def findMask(name = "sfz"):
    inF = ROOT.TFile.Open("SMWorkspace.root")
    iter = inF.Get("w").pdf("model_b").getVariables().createIterator()
    var = iter.Next()
    masks = []
    while(var):
        if name in var.GetName() and "mask" in var.GetName():
            masks.append(var.GetName() + '=1')
        var = iter.Next()
    return masks
