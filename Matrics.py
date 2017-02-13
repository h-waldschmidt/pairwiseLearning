import math
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def DCG(truth):
    n = len(truth)
    res = 0
    for i in range(n):
        res += (2**truth[i] - 1.) / (math.log(i+2., 2.))
    if (n < 1):
        return 0.
    return float(res) / n

def NDCG(truth):
    dcg = DCG(truth)
    perfect_DCG = DCG(sorted(truth, key=lambda x: -x))
    if (perfect_DCG < 1e-19):
        return 0.
    return dcg / perfect_DCG

def N_correct_pairs(truth):
    correct_pairs = 0
    n_pairs = 0
    for i in range(len(truth)):
        for j in range(i+1, len(truth)):
            if (truth[i] != truth[j]):
                n_pairs += 1
                if (truth[i] > truth[j]):
                    correct_pairs += 1
    n_pairs += 1e-10
    return float(correct_pairs)/ n_pairs

def Precision(truth, n_points):
    if (len(truth) < n_points):
        return 0
    else:
        return sum(truth[:n_points]) / float(n_points)

def receive_answer(user, item, min_rating, max_rating, item_bias):
    u_answers = np.rint(np.dot(item, user) + item_bias)
    if (u_answers < min_rating): u_answers = min_rating
    if (u_answers > max_rating): u_answers = max_rating
    return u_answers

def BestItem(items, user, used_items, items_bias, threshold = 1.):
    #print(items.shape, user.shape)
    items_bias_ = np.array(items_bias)
    items_bias_[items_bias > threshold] = -1000
    items_bias_[items_bias < -threshold] = -1000
    items_bias_[used_items] = -1000
     
    preferences = np.dot(items, user) + items_bias_
    return np.argmax(preferences)

    best_item = 0
    preference = -1000
    for i in range(len(items)):
        if i not in used_items and items_bias[i] < threshold and items_bias[i] > -1 * threshold:
            estim_preferense = np.dot(items[i], user)
            estim_preferense += items_bias[i]
            if (estim_preferense > preference):
                del_ = items[i]
                preference = estim_preferense
                best_item = i
    return best_item

def GetRecommendetList(items, user_estim, items_bias, user):
    user_estim.reshape([user_estim.shape[0], 1])
    items_bias.reshape([len(items_bias), 1])
    truth = np.dot(user_estim, items.T) + items_bias
    item_list = np.argsort(-truth)
    real_truth = np.dot(user, items.T) + items_bias
    real_truth = np.rint(real_truth)
    real_truth[real_truth > 1] = 1.
    real_truth[real_truth < -1]  = -1.
    return item_list, real_truth[item_list]

def GetSERP(ratings):
    ratings_ = np.argsort(ratings)
    n_ones = np.sum(ratings > 0)
    n_bad = np.sum(ratings < 0)
    n_ex = min(n_ones, n_bad)
    zeros = ratings_[0:n_bad]
    np.random.shuffle(zeros)
    ones = ratings_[n_bad:]
    np.random.shuffle(ones)
    try:
        ones = ones[0]
        zeros = zeros[:9]
    except:
        return np.zeros(10)
    res = np.append(ones, zeros)
    return res

def UserEstimation(questions_items, items, items_bias, user, n_q):
    questions_items1 = questions_items.T
    questions = (items[questions_items1[0]] - items[questions_items1[1]])[:n_q]
    bias = (items_bias[questions_items1[0]] - items_bias[questions_items1[1]])[:n_q]
    answers = np.rint(np.dot(questions, user) + bias)
    answers[answers > 2] = 2.
    answers[answers < -2] = -2.
    answers -= bias
    #if (n_q == 30):
    #    print(np.trace(np.linalg.inv(np.dot(questions.T, questions) +
    #                                 0.001 * np.eye(questions.shape[1]))))

    inv_questions = np.linalg.inv(np.dot(questions.T, questions) + 0.001 * np.eye(questions.shape[1]))
    return np.dot(inv_questions,
                        np.dot(answers, questions))

def Test(questions_items, n_q, items, items_bias, user, user_estim, ratings, all_items, all_items_bias):
    #print(questions_items.shape)
    if(n_q==0):
        user_estim = user
    if(n_q > 1):
        #user_estim = user
        user_estim = UserEstimation(questions_items, all_items, all_items_bias, user, n_q-1)
    # test all
    my_recommendation_list, truth = GetRecommendetList(items, user_estim, items_bias, user)
    a = ratings[my_recommendation_list]
    #a = a[:10] > 0
    dif = 1 - abs(np.dot(user, user_estim) / math.sqrt(np.dot(user, user) * np.dot(user_estim, user_estim)))
    dist = np.dot(dif, dif.T)
    truth = ratings[my_recommendation_list]
    #print(truth)
    NDCG_ = NDCG((truth + 1) / 2.)
    precision10 = Precision((truth + 1) / 2., 10)
    correct_pairs = N_correct_pairs(truth)
    return dist, NDCG_, correct_pairs, precision10
    #print(NDCG_)
    #return NDCG_ ,0 , 0



