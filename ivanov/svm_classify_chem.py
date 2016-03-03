'''
Created on Feb 17, 2016

@author: Ivan Ivanov
'''
from ivanov import statistics
import commands

# comm_prefix = ""
comm_prefix = "~/Programs/svm_light/"

path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/nci_hiv/cv_data_A_vs_M/"

_id = "tanh"
kernel = 3
g = 0.
s = 0.001
r = 0.001
d = 0.
wl_range = range(0, 12)
crossval_folds = 10

output_file = path + "scores_A_vs_M_" + _id

def compute_scores(w):
    auc_avg = 0.
    acc_avg = 0.
    prec_avg = 0.
    rec_avg = 0.
    
    form = {
        "path": path,
        "id": _id,
        "k": 0,
        "w": w,
    }
    
    for k in range(1, crossval_folds + 1):
        form["k"] = k
        auc, acc, prec, rec = statistics.all_scores_from_files("{path}fold_{k}/val_wl_{w}".format(**form), "{path}models/predict_{id}_k_{k}".format(**form))
        auc_avg += auc
        acc_avg += acc
        prec_avg += prec
        rec_avg += rec
    
    auc_avg /= crossval_folds
    acc_avg /= crossval_folds
    prec_avg /= crossval_folds
    rec_avg /= crossval_folds
    
    return w, auc_avg, acc_avg, prec_avg, rec_avg

def svm_crossval():
    print "Start:", _id
    
    form = {
        "prefix": comm_prefix,
        "k": 0,
        "w": -1,
        "id": _id,
        "kernel": kernel,
        "g": g,
        "s": s,
        "r": r,
        "d": d,
        "path": path
    }
    
    with open(output_file, "w") as fl:
        fl.write("wl_iter,auc,accuracy,precision,recall\n")
        for w in wl_range:
            form["w"] = w
            k_range = range(1, crossval_folds + 1)
            for k in k_range:
                print _id, w, k
                form["k"] = k
                learn_comm = "{prefix}svm_learn -t {kernel} -g {g} -s {s} -r {r} -d {d} {path}fold_{k}/train_wl_{w} {path}models/model_{id}".format(**form)
                predict_comm = "{prefix}svm_classify {path}fold_{k}/val_wl_{w} {path}models/model_{id} {path}models/predict_{id}_k_{k}".format(**form)
                commands.getstatusoutput(learn_comm)
                commands.getstatusoutput(predict_comm)
            scores = compute_scores(w)
            print "Scores:", scores
            fl.write(",".join(map(lambda x: str(x), scores)) + "\n")
            fl.flush()
    
    print "Done:", _id

if __name__ == '__main__':
    svm_crossval()
    print "Done!"
