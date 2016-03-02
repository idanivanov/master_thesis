'''
Created on Feb 17, 2016

@author: Ivan Ivanov
'''
from ivanov import statistics
import commands

path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/nci_hiv/cv_data_A_vs_M/"
output_file = path + "scores_A_vs_M_RBF_001"

kernel = 2 # TODO: currently only for RBF
g = 0.001
wl_range = range(0, 12)
crossval_folds = 10

def compute_scores(w, g):
    auc_avg = 0.
    acc_avg = 0.
    prec_avg = 0.
    rec_avg = 0.
    
    for k in range(1, crossval_folds + 1):
        auc, acc, prec, rec = statistics.all_scores_from_files(path + "fold_{0}/val_wl_{1}".format(k, w), path + "models/predict_rbf_{2}_k_{0}".format(k, w, g[2:]))
        auc_avg += auc
        acc_avg += acc
        prec_avg += prec
        rec_avg += rec
    
    auc_avg /= crossval_folds
    acc_avg /= crossval_folds
    prec_avg /= crossval_folds
    rec_avg /= crossval_folds
    
    return w, auc_avg, acc_avg, prec_avg, rec_avg

def svm_crossval(g):
    print "Start:", g
    with open(output_file, "w") as fl:
        fl.write("wl_iter,auc,accuracy,precision,recall\n")
        for w in wl_range:
            k_range = range(1, crossval_folds + 1)
            for k in k_range:
                print g, w, k
                learn_comm = "svm_learn -t {2} -g {3} {5}fold_{0}/train_wl_{1} {5}models/model_rbf_{4}".format(k, w, kernel, g, g[2:], path)
                commands.getstatusoutput(learn_comm)
                predict_comm = "svm_classify {3}fold_{0}/val_wl_{1} {3}models/model_rbf_{2} {3}models/predict_rbf_{2}_k_{0}".format(k, w, g[2:], path)
                commands.getstatusoutput(predict_comm)
            scores = compute_scores(w, g)
            print "Scores:", scores
            fl.write(",".join(map(lambda x: str(x), scores)) + "\n")
            fl.flush()
    
    print "Done:", g

if __name__ == '__main__':
    svm_crossval(str(g))
    print "Done!"
