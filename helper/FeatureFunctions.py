import numpy as np

def polynomial_features(X, args = {"degree":2, "interaction":False}):
    if type(X) == float or type(X) == int:
        features = [1]
        if args["interaction"]:
            pass
        else:
            for d in range(1, args["degree"]):
                tmp = X**d
                features.append(tmp)
        features = np.array(features).reshape(1,-1)
    else:
        features = np.ones(X.shape[0]).reshape(-1,1)
        if args["interaction"]:
            pass
        else:
            for i in range(X.shape[1]):
                for d in range(1, args["degree"]+1):
                    tmp = X[:, i]**d
                    tmp = tmp.reshape(-1,1)
                    features = np.concatenate((features, tmp), axis=1)
    return features