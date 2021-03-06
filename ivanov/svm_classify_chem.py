'''
Created on Feb 17, 2016

@author: Ivan Ivanov
'''
from ivanov import statistics
import numpy as np
import commands

comm_prefix = ""
# comm_prefix = "~/Programs/svm_light/"

path = "/home/stud/ivanovi/Thesis/svm/nci_hiv/cv_data_A_vs_I/"
# path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/nci_hiv/cv_data_A_vs_I/"

_id = "A_vs_I_rbf_1"
kernel = 2
# g = 0.
# s = 0.001
# r = 0.001
# d = 0.
wl_range = range(8, 11)
g_range = np.arange(0.0045, 0.005, 0.0001)
crossval_folds = 10

output_file = path + "scores_" + _id

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

def svm_crossval_wl_iter(g, s=0., r=0., d=0.):
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
    
    with open(output_file, "a") as fl:
#         fl.write("g,wl_iter,auc,accuracy,precision,recall\n")
        for w in wl_range:
            form["w"] = w
            k_range = range(1, crossval_folds + 1)
            for k in k_range:
                print _id, g, w, k
                form["k"] = k
                learn_comm = "{prefix}svm_learn -t {kernel} -g {g} -s {s} -r {r} -d {d} {path}fold_{k}/train_wl_{w} {path}models/model_{id}".format(**form)
                predict_comm = "{prefix}svm_classify {path}fold_{k}/val_wl_{w} {path}models/model_{id} {path}models/predict_{id}_k_{k}".format(**form)
                commands.getstatusoutput(learn_comm)
                commands.getstatusoutput(predict_comm)
            scores = compute_scores(w)
            print "Scores:", scores
            fl.write(str(g) + ", " + ",".join(map(lambda x: str(x), scores)) + "\n")
            fl.flush()
    
    print "Done:", _id

def svm_crossval():
    for g in g_range:
        svm_crossval_wl_iter(g)

if __name__ == '__main__':
    svm_crossval()
    print "Done!"
