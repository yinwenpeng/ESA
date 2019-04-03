import time
from load_data import load_yahoo_and_labelnames
from ESA import load_ESA_sparse_matrix, divide_sparseMatrix_by_list_row_wise, multiply_sparseMatrix_by_list_row_wise
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from scipy.sparse import vstack
import numpy as np
from operator import itemgetter
from scipy.special import softmax

all_texts, all_labels, all_word2DF, labelnames = load_yahoo_and_labelnames()
ESA_sparse_matrix = load_ESA_sparse_matrix().tocsr()
# ESA_sparse_matrix_2_dict = {}
#
# def ESA_sparse_matrix_into_dict():
#     global ESA_sparse_matrix_2_dict
#     for i in range(ESA_sparse_matrix.shape[0]):
#         ESA_sparse_matrix_2_dict[i] = ESA_sparse_matrix.getrow(i)
#     print('ESA_sparse_matrix_into_dict succeed')


def text_idlist_2_ESAVector(idlist, text_bool):
    # sub_matrix = ESA_sparse_matrix[idlist,:]
    # return  sub_matrix.mean(axis=0)
    # matrix_list = []
    # for id in idlist:
    #     matrix_list.append(ESA_sparse_matrix_2_dict.get(id))
    # stack_matrix = vstack(matrix_list)
    # return  stack_matrix.mean(axis=0)
    # print('idlist:', idlist)
    if text_bool:
        sub_matrix = ESA_sparse_matrix[idlist,:]
        # myvalues = list(itemgetter(*idlist)(all_word2DF))
        myvalues = [all_word2DF.get(id) for id in idlist]
        weighted_matrix = divide_sparseMatrix_by_list_row_wise(sub_matrix, myvalues)
        return  weighted_matrix.sum(axis=0)
    else: #label names
        sub_matrix = ESA_sparse_matrix[idlist,:]
        return  sub_matrix.sum(axis=0)

def text_idlist_2_ESAVector_attention(idlist, text_bool, label_veclist):


    sub_matrix = ESA_sparse_matrix[idlist,:]
    result_veclist = []
    for vec in label_veclist:
        cos = cosine_similarity(sub_matrix, vec)
        att_matrix = multiply_sparseMatrix_by_list_row_wise(sub_matrix, softmax(cos))
        result_veclist.append(att_matrix.sum(axis=0))

    return  result_veclist

    # if text_bool:
    #     sub_matrix = ESA_sparse_matrix[idlist,:]
    #     myvalues = [all_word2DF.get(id) for id in idlist]
    #     weighted_matrix = divide_sparseMatrix_by_list_row_wise(sub_matrix, myvalues)
    #     return  weighted_matrix.sum(axis=0)
    # else: #label names
    #     sub_matrix = ESA_sparse_matrix[idlist,:]
    #     return  sub_matrix.sum(axis=0)

def ESA_cosine():
    label_veclist = []
    for i in range(len(labelnames)):
        labelname_idlist = labelnames[i]
        label_veclist.append(text_idlist_2_ESAVector(labelname_idlist, False))
    # print(label_veclist)
    print('all labelnames are in vec succeed')
    labels = all_labels[0]
    sample_size = len(labels)
    print('total test size:', sample_size)
    hit_size = 0
    co=0
    start_time = time.time()
    for i in range(sample_size):
        text_idlist = all_texts[0][i]
        text_vec = text_idlist_2_ESAVector(text_idlist, True)
        cos_array=cosine_similarity(text_vec, np.vstack(label_veclist))
        max_id = np.argmax(cos_array, axis=1)
        if max_id[0] == labels[i]:
            hit_size+=1
        co+=1
        print(co, '...', hit_size/sample_size, hit_size/co)
        if co%10==0:
            spend_time = (time.time()-start_time)/60.0
            print('\t\t\t\t\t',spend_time, 'mins')
    acc = hit_size/sample_size
    print('acc:', acc)

def ESA_cosine_attention():
    label_veclist = []
    for i in range(len(labelnames)):
        labelname_idlist = labelnames[i]
        label_veclist.append(text_idlist_2_ESAVector(labelname_idlist, False))
    # print(label_veclist)
    print('all labelnames are in vec succeed')
    labels = all_labels[0]
    sample_size = len(labels)
    print('total test size:', sample_size)
    hit_size = 0
    co=0
    start_time = time.time()
    for i in range(sample_size):
        text_idlist = all_texts[0][i]
        text_veclist = text_idlist_2_ESAVector_attention(text_idlist, True, label_veclist)
        cos_array=cosine_similarity(np.vstack(text_veclist), np.vstack(label_veclist))
        print('cos_array:',cos_array)
        print('diagonal:', cos_array.diagonal(), 'ground truth:', labels[i])
        # exit(0)
        max_id = np.argmax(cos_array.diagonal())
        # print('max_id:',max_id)
        # exit(0)
        if max_id == labels[i]:
            hit_size+=1
        co+=1
        print(co, '...', hit_size/sample_size, hit_size/co)
        if co%10==0:
            spend_time = (time.time()-start_time)/60.0
            print('\t\t\t\t\t',spend_time, 'mins')
    acc = hit_size/sample_size
    print('acc:', acc)

if __name__ == '__main__':
    ESA_cosine()
    # ESA_cosine_attention()
