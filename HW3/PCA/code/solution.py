import torch
import torch.nn as nn
import numpy as np
import pickle, tqdm, os, time

'''
Homework3: Principal Component Analysis and Autoencoders

Useful numpy functions
----------------------
In this assignment, you may want to use following helper functions:
- np.linalg.svd(): compute the singular value decomposition on a given matrix. 
- np.dot(): matrices multiplication operation.
- np.mean(): compute the mean value on a given matrix.
- np.zeros(): generate a all '0' matrix with a certain shape.
- np.expand_dims: expand the dimension of an array at the referred axis.
- np.squeeze: Remove single-dimensional entries from the shape of an array. 
- np.transpose(): matrix transpose operation.
- np.linalg.norm(): compute the norm value of a matrix. You may use it for the reconstruct_error function.

Pytorch functions and APIs you may need
------------------------------------------
torch.empty
torch.mm
torch.transpose
nn.Parameter
nn.init.kaiming_normal_
nn.Tanh
nn.ReLU
nn.Sigmoid
'''


class PCA():
    '''
    Important!! Read before starting.
    1. To coordinate with the note at http://people.tamu.edu/~sji/classes/PCA.pdf,
    we set the input shape to be [256, n_samples].
    2. According to the note, input matrix X should be centered before doing SVD

    '''

    def __init__(self, X, n_components):
        '''
        Args:
            X: The data matrix of shape [n_features, n_samples].
            n_components: The number of principal components. A scaler number.
        '''

        self.n_components = n_components
        self.X = X
        self.Up, self.Xp = self._do_pca()

    def _do_pca(self):
        '''
        To do PCA decomposition.
        Returns:
            Up: Principal components (transform matrix) of shape [n_features, n_components].
            Xp: The reduced data matrix after PCA of shape [n_components, n_samples].
        '''
        ### YOUR CODE HERE
        normalized_X = self.X - self.X.mean(axis=1, keepdims=True)
        cov_X = np.cov(normalized_X)
        U, sigma, V = np.linalg.svd(cov_X)

        Up = U[:, :self.n_components]  # [n_features, n_components]
        Xp = np.dot(normalized_X.T, Up)  # [n_samples, n_features] . [n_features, n_components]
        Xp = Xp.T

        # print(f"shape of Up={Up.shape} and Xp={Xp.shape}")
        ### END YOUR CODE
        return Up, Xp

    def get_reduced(self, X=None):
        '''
        To return the reduced data matrix.
        Args:
            X: The data matrix with shape [n_features, n_any] or None. 
               If None, return reduced training X.
        Returns:
            Xp: The reduced data matrix of shape [n_components, n_any].
        '''
        if X is None:
            return self.Xp, self.Up
        else:
            return self.Up.T @ X, self.Up

    def reconstruction(self, Xp):
        '''
        To reconstruct reduced data given principal components Up.

        Args:
        Xp: The reduced data matrix after PCA of shape [n_components, n_samples].

        Return:
        X_re: The reconstructed matrix of shape [n_features, n_samples].
        '''
        ### YOUR CODE HERE
        # Up : [n_features, n_components]
        # Xp : [n_components, n_samples]
        X_re = np.dot(self.Up, Xp)
        X_re = X_re + self.X.mean(axis=1, keepdims=True)
        ### END YOUR CODE
        return X_re


def frobeniu_norm_error(A, B):
    '''
    To compute Frobenius norm's square of the matrix A-B. It can serve as the
    reconstruction error between A and B, or can be used to compute the 
    difference between A and B.

    Args: 
    A & B: Two matrices needed to be compared with. Should be of same shape.

    Return: 
    error: the Frobenius norm's square of the matrix A-B. A scaler number.
    '''
    return np.linalg.norm(A - B)


class AE(nn.Module):
    '''
    Important!! Read before starting.
    1. To coordinate with the note at http://people.tamu.edu/~sji/classes/PCA.pdf and
    compare with PCA, we set the shape of input to the network as [256, n_samples].
    2. Do not do centering. Even though X in the note is the centered data, the neural network is 
    capable to learn this centering process. So unlike PCA, we don't center X for autoencoders,
    and we will still get the same results.
    3. Don't change or slightly change hyperparameters like learning rate, batch size, number of
    epochs for 5(e), 5(f) and 5(g). But for 5(h), you can try more hyperparameters and achieve as good results
    as you can.

    '''

    def __init__(self, d_hidden_rep):
        '''
        Args:
            d_hidden_rep: The dimension for the hidden representation in AE. A scaler number.
            n_features: The number of initial features, 256 for this dataset.
            
        Attributes:
            X: A torch tensor of shape [256, None]. A placeholder 
               for input images. "None" refers to any batch size.
            out_layer: A torch tensor of shape [256, None]. Output signal
               of network
            initializer: Initialize the trainable weights.
        '''
        super(AE, self).__init__()
        self.d_hidden_rep = d_hidden_rep
        self.n_features = 256
        self._network()

    def _network(self):
        '''

        You are free to use the listed functions and APIs from torch or torch.nn:
            torch.empty
            nn.Parameter
            nn.init.kaiming_normal_
        
        You need to define and initialize weights here.
            
        '''

        ### YOUR CODE HERE

        '''
        Note: you should include all the three variants of the networks here. 
        You can comment the other two when you running one, but please include 
        and uncomment all the three in you final submissions.
        '''

        # Note: here for the network with weights sharing. Basically you need to follow the ...?
        W = torch.empty(self.n_features, self.d_hidden_rep)
        self.w = nn.Parameter(nn.init.kaiming_normal_(W))

        # Note: here for the network without weights sharing
        W_encoder = torch.empty(self.n_features, self.d_hidden_rep)
        self.w = nn.Parameter(nn.init.kaiming_normal_(W_encoder))

        W_decoder = torch.empty(self.d_hidden_rep, self.n_features)
        self.w_decoder = nn.Parameter(nn.init.kaiming_normal_(W_decoder))

        # Note: here for the network with more layers and nonlinear functions
        # structure == encoder1 --> encoder2 --> hidden rep --> decoder1 --> decoder2
        W_encoder1 = torch.empty(self.n_features, 2 * self.d_hidden_rep)
        self.w_encoder1 = nn.Parameter(nn.init.kaiming_normal_(W_encoder1))

        W_encoder2 = torch.empty(2 * self.d_hidden_rep, self.d_hidden_rep)
        self.w = nn.Parameter(nn.init.kaiming_normal_(W_encoder2))   # w == w_encoder2

        W_decoder1 = torch.empty(self.d_hidden_rep, 2 * self.d_hidden_rep)
        self.w_decoder1 = nn.Parameter(nn.init.kaiming_normal_(W_decoder1))

        W_decoder2 = torch.empty(2 * self.d_hidden_rep, self.n_features)
        self.w_decoder2 = nn.Parameter(nn.init.kaiming_normal_(W_decoder2))
        ### END YOUR CODE

    def _forward(self, X):
        '''

        You are free to use the listed functions and APIs from torch and torch.nn:
            torch.mm
            torch.transpose
            nn.Tanh
            nn.ReLU
            nn.Sigmoid
        
        Args:
            X: A torch tensor of shape [n_features, batch_size].
                for input images.

        Returns:
            out: A torch tensor of shape [n_features, batch_size].
            
        '''

        ### YOUR CODE HERE

        '''
        Note: you should include all the three variants of the networks here. 
        You can comment the other two when you running one, but please include 
        and uncomment all the three in you final submissions.
        '''

        # Note: here for the network with weights sharing. Basically you need to follow the
        # formula (WW^TX) in the note at http://people.tamu.edu/~sji/classes/PCA.pdf .
        encoder = torch.mm(self.w.T, X)
        decoder = torch.mm(self.w, encoder)
        return decoder

        # Note: here for the network without weights sharing
        encoder = torch.mm(self.w.T, X)
        decoder = torch.mm(self.w_decoder.T, encoder)
        return decoder

        # Note: here for the network with more layers and nonlinear functions
        # structure == encoder1 --> encoder2 --> hidden rep --> decoder1 --> decoder2
        encoder1 = torch.mm(self.w_encoder1.T, X)
        encoder1 = torch.relu(encoder1)
        encoder2 = torch.mm(self.w.T, encoder1)
        decoder1 = torch.mm(self.w_decoder1.T, encoder2)
        decoder1 = torch.relu(decoder1)
        decoder2 = torch.mm(self.w_decoder2.T, decoder1)
        return decoder2
        ### END YOUR CODE

    def _setup(self):
        '''
        Model and training setup.
 
        Attributes:
            loss: MSE loss function for computing on the current batch.
            optimizer: torch.optim. The optimizer for training
                the model. Different optimizers use different gradient
                descend policies.
        '''
        self.loss = nn.MSELoss(reduction='mean')
        self.optimizer = torch.optim.Adam(self.parameters(), lr=0.001)

    def train(self, x_train, x_valid, batch_size, max_epoch):

        '''
        Autoencoder is an unsupervised learning method. To compare with PCA,
        it's ok to use the whole training data for validation and reconstruction.
        '''

        self._setup()

        num_samples = x_train.shape[1]
        num_batches = int(num_samples / batch_size)

        num_valid_samples = x_valid.shape[1]
        num_valid_batches = (num_valid_samples - 1) // batch_size + 1

        print('---Run...')
        for epoch in range(1, max_epoch + 1):

            # To shuffle the data at the beginning of each epoch.
            shuffle_index = np.random.permutation(num_samples)
            curr_x_train = x_train[:, shuffle_index]

            # To start training at current epoch.
            loss_value = []
            qbar = tqdm.tqdm(range(num_batches))
            for i in qbar:
                batch_start_time = time.time()

                start = batch_size * i
                end = batch_size * (i + 1)
                x_batch = curr_x_train[:, start:end]

                x_batch_tensor = torch.tensor(x_batch).float()
                x_batch_re_tensor = self._forward(x_batch_tensor)
                loss = self.loss(x_batch_re_tensor, x_batch_tensor)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                if not i % 10:
                    qbar.set_description(
                        'Epoch {:d} Loss {:.6f}'.format(
                            epoch, loss.detach().item()))

            # To start validation at the end of each epoch.
            loss = 0
            print('Doing validation...', end=' ')

            with torch.no_grad():
                for i in range(num_valid_batches):
                    start = batch_size * i
                    end = min(batch_size * (i + 1), x_valid.shape[1])
                    x_valid_batch = x_valid[:, start:end]

                    x_batch_tensor = torch.tensor(x_valid_batch).float()
                    x_batch_re_tensor = self._forward(x_batch_tensor)
                    loss = self.loss(x_batch_re_tensor, x_batch_tensor)

            print('Validation Loss {:.6f}'.format(loss.detach().item()))

    def get_params(self):
        """
        Get parameters for the trained model.
        
        Returns:
            final_w: A numpy array of shape [n_features, d_hidden_rep].
        """
        return self.w.detach().numpy()

    def reconstruction(self, X):
        '''
        To reconstruct data. You’re required to reconstruct one by one here,
        that is to say, for one loop, input to the network is of the shape [n_features, 1].
        Args:
            X: The data matrix with shape [n_features, n_any], a numpy array.
        Returns:
            X_re: The reconstructed data matrix, which has the same shape as X, a numpy array.
        '''

        # define X_re
        X_re = list()
        _, n_samples = X.shape

        with torch.no_grad():
            for i in range(n_samples):
                ### YOUR CODE HERE
                n_features, _ = X.shape
                curr_X = X[:, i].reshape(n_features, 1)
                # Note: Format input curr_X to the shape [n_features, 1]

                ### END YOUR CODE
                curr_X_tensor = torch.tensor(curr_X).float()
                curr_X_re_tensor = self._forward(curr_X_tensor)
                ### YOUR CODE HERE

                X_re.append(curr_X_re_tensor.numpy())
                # Note: To achieve final reconstructed data matrix with the shape [n_features, n_any].

            X_re = np.array(X_re).T
            ### END YOUR CODE

        return X_re
