import torch
import torch.nn as nn
import numpy as np
import time

"""
This script implements a kernel logistic regression model, a radial basis function network model
and a two-layer feed forward network.
"""

class Kernel_Layer(nn.Module):

    def __init__(self, sigma, hidden_dim=None):
        """
        Set hyper-parameters.
        Args:
            sigma: the sigma for Gaussian kernel (radial basis function)
            hidden_dim: the number of "kernel units", default is None, then the number of "kernel units"
                                       will be set to be the number of training samples
        """
        super(Kernel_Layer, self).__init__()
        self.sigma = sigma
        self.hidden_dim = hidden_dim
    
    def reset_parameters(self, X):
        """
        Set prototypes (stored training samples or "representatives" of training samples) of
        the kernel layer.
        """
        if self.hidden_dim is not None:
            X = self._k_means(X)
        self.prototypes = nn.Parameter(torch.tensor(X).float(), requires_grad=False)
    
    def _k_means(self, X):
        """
        K-means clustering
        
        Args:
            X: A Numpy array of shape [n_samples, n_features].
        
        Returns:
            centroids: A Numpy array of shape [self.hidden_dim, n_features].
        """
        ### YOUR CODE HERE
        tX = torch.as_tensor(X)
        centroids = tX[torch.randint(0, X.shape[0], (self.hidden_dim,)), :]
        previous_assign = torch.randint(0, self.hidden_dim, (X.shape[0],))

        for acc in range(1, 2000):
            dists = torch.cdist(tX, centroids)  # default is 2-norm
            current_assign = dists.argmin(dim=1)
            if current_assign.eq(previous_assign).all():
                break
            else:
                previous_assign = current_assign
            for n in range(self.hidden_dim):
                centroids[n, :] = torch.mean(tX[current_assign.eq(n), :], dim=0)
        ### END YOUR CODE
        return centroids
    
    def forward(self, x):
        """
        Compute Gaussian kernel (radial basis function) of the input sample batch
        and self.prototypes (stored training samples or "representatives" of training samples).

        Args:
            x: A torch tensor of shape [batch_size, n_features]
        
        Returns:
            A torch tensor of shape [batch_size, num_of_prototypes]
        """
        assert x.shape[1] == self.prototypes.shape[1]
        ### YOUR CODE HERE
        # Basically you need to follow the equation of radial basis function
        # in the section 5 of note at http://people.tamu.edu/~sji/classes/nnkernel.pdf
        batch_size, n_features = x.shape
        size = (batch_size, self.prototypes.shape[0], n_features)

        x = x.unsqueeze(1).expand(size)
        p = self.prototypes.unsqueeze(0).expand(size)
        two_norm_squared = (x - p).pow(2).sum(-1).pow(0.5)

        kernel_result = torch.exp(-1 * two_norm_squared / (2 * (np.power(self.sigma, 2))))
        return kernel_result
        ### END YOUR CODE


class Kernel_LR(nn.Module):

    def __init__(self, sigma, hidden_dim):
        """
        Define network structure.

        Args:
            sigma: used in the kernel layer.
            hidden_dim: the number of prototypes in the kernel layer,
                                       in this model, hidden_dim has to be equal to the 
                                       number of training samples.
        """
        super(Kernel_LR, self).__init__()
        self.hidden_dim = hidden_dim
        ### YOUR CODE HERE
        # Use pytorch nn.Sequential object to build a network composed of a
        # kernel layer (Kernel_Layer object) and a linear layer (nn.Linear object)

        # Remember that kernel logistic regression model uses all training samples
        # in kernel layer, so set 'hidden_dim' argument to be None when creating
        # a Kernel_Layer object.

        # How should we set the "bias" argument of nn.Linear? 

        self.net = nn.Sequential(
            Kernel_Layer(sigma),
            nn.Linear(hidden_dim, 1, False)
        )
        ### END YOUR CODE

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: A torch tensor of shape [batch_size, n_features]
        
        Returns:
            A torch tensor of shape [batch_size, 1]
        """
        return self.net(x)
    
    def reset_parameters(self, X):
        """
        Initialize the weights of the linear layer and the prototypes of the kernel layer.

        Args:
            X: A Numpy array of shape [n_samples, n_features], training data matrix.
        """
        assert X.shape[0] == self.hidden_dim
        for layer in self.net:
            if hasattr(layer, 'reset_parameters'):
                if isinstance(layer, Kernel_Layer):
                    layer.reset_parameters(X)
                else:
                    layer.reset_parameters()



class RBF(nn.Module):

    def __init__(self, sigma, hidden_dim):
        """
        Define network structure.

        Args:
            sigma: used in the kernel layer.
            hidden_dim: the number of prototypes in the kernel layer,
                                       in this model, hidden_dim is a user-specified hyper-parameter.
        """
        super(RBF, self).__init__()
        ### YOUR CODE HERE
        # Use pytorch nn.Sequential object to build a network composed of a
        # kernel layer (Kernel_Layer object) and a linear layer (nn.Linear object)
        # How should we set the "bias" argument of nn.Linear? 
        self.net = nn.Sequential(
            Kernel_Layer(sigma, hidden_dim),
            nn.Linear(hidden_dim, 1, False)
        )
        ### END CODE HERE

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: A torch tensor of shape [batch_size, n_features]
        
        Returns:
            A torch tensor of shape [batch_size, 1]
        """
        return self.net(x)
    
    def reset_parameters(self, X):
        """
        Initialize the weights of the linear layer and the prototypes of the kernel layer.

        Args:
            X: A Numpy array of shape [n_samples, n_features], training data matrix.
        """
        for layer in self.net:
            if hasattr(layer, 'reset_parameters'):
                if isinstance(layer, Kernel_Layer):
                    layer.reset_parameters(X)
                else:
                    layer.reset_parameters()



class FFN(nn.Module):

    def __init__(self, input_dim, hidden_dim):
        """
        Define network structure.

        Args:
            input_dim: number of features of each input.
            hidden_dim: the number of hidden units in the hidden layer, a user-specified hyper-parameter.
        """
        super(FFN, self).__init__()
        ### YOUR CODE HERE
        # Use pytorch nn.Sequential object to build a network composed of
        # two linear layers (nn.Linear object)
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim, True),
            nn.Linear(hidden_dim, 1, True)
        )
        ### END CODE HERE

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: A torch tensor of shape [batch_size, n_features]
        
        Returns:
            A torch tensor of shape [batch_size, 1]
        """
        return self.net(x)

    def reset_parameters(self):
        """
        Initialize the weights of the linear layers.
        """
        for layer in self.net:
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()