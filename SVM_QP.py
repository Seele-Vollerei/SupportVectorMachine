import numpy as np
import matplotlib.pyplot as plt
from cvxopt import matrix, solvers
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.preprocessing import PolynomialFeatures



class SVM_QP:
    def __init__(self, kernel=None,gamma=None,degree=2):
        self.kernel = kernel
        if self.kernel == 'rbf':
            self.gamma=gamma
        if self.kernel == 'poly':
            self.degree = degree
    
    def transform(self,x):
        if self.kernel == 'rbf':
            x_feature = rbf_kernel(x,self.xtrain,gamma=self.gamma)
            x = np.concatenate((x,x_feature),axis = -1)
        elif self.kernel == 'poly':
            x = PolynomialFeatures(self.degree,include_bias=False).fit_transform(x)
        return x

    def fit(self,x,y,c=None):
        self.xtrain = x
        x = self.transform(x)
        solvers.options['show_progress'] = False
        if c is None:
            return self.fit_hard(x,y)
        else:
            return self.fit_soft(x,y,c)

    def fit_hard(self,x,y):
        # hard margin
        n,m = x.shape
        
        # define varaiables
        p = np.zeros((m+1,m+1))
        for i in range(1,m+1):
            p[i,i] = 1
        q = np.zeros(m+1)
        h = -np.ones(n)
        g = np.append(np.ones((n,1)), x, axis=1)
        g *= -y[:,np.newaxis]

        # convert to cvxopt datatype
        p = matrix(p)
        q = matrix(q)
        g = matrix(g)
        h = matrix(h)

        # run solver
        self.sol = solvers.qp(p,q,g,h)

        self.beta = np.array(self.sol['x'])
        return self.sol

    def fit_soft(self,x,y,c):
        # soft margin
        n,m = x.shape

        # define varaiables
        p = np.zeros((m+n+1,m+n+1))
        for i in range(n+1,m+n+1):
            p[i,i] = 1
        q = np.concatenate((c*np.ones(n),np.zeros(m+1)))
        h = np.concatenate((-np.ones(n),np.zeros(n)))
        gleft = -np.vstack((np.eye(n),np.eye(n)))
        gtopr = np.append(np.ones((n,1)), x, axis=1)*-y[:,np.newaxis]
        gbotr = np.zeros((n,m+1))
        gright = np.vstack((gtopr,gbotr))
        g = np.hstack((gleft,gright))


        # convert to cvxopt datatype
        p = matrix(p)
        q = matrix(q)
        g = matrix(g)
        h = matrix(h)

        # run solver
        self.sol = solvers.qp(p,q,g,h)

        self.beta = np.array(self.sol['x'])[n:]
        return self.sol



    def predict(self,x):
        x = self.transform(x)
        pred = self.beta[0] + x.dot(self.beta[1:]) > 0
        pred = pred.reshape(-1,)
        pred = pred*2 - 1
        return pred 
    
    def error(self,x,y):
        pred = self.predict(x)
        return np.mean(pred != y)


    def plot(self,X,y,title=''):
        plt.figure(figsize= (10,6))
        
        x_min, x_max = X[:,0].min() - 1, X[:,0].max() + 1
        y_min, y_max = X[:,1].min() - 1, X[:,1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.05), np.arange(y_min, y_max, 0.05))
        Z=self.predict(np.c_[xx.ravel(), yy.ravel()])
        plt.contourf(xx,yy,np.asarray(Z).reshape(xx.shape),cmap=plt.cm.coolwarm,alpha=0.6 )

        plt.scatter(np.asarray(X)[:,0], np.asarray(X)[:,1], c=y, cmap=plt.cm.coolwarm, s = 50)
        plt.title(title)

        plt.show()