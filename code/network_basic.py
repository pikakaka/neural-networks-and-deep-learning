"""
network_basic
~~~~~~~~~~~~~

A module to implement the stochastic gradient descent learning
algorithm for a feedforward neural network.  Gradients are calculated
using backpropagation.  Note that I have focused on making the code
simple, easily readable, and easily modifiable.  It is not optimized,
and omits many desirable features.
"""

#### Libraries
# Standard library
import random

# Third-party libraries
import numpy as np

class Network():

    def __init__(self, sizes):
        """The list ``sizes`` contains the number of neurons in the
        respective layers of the network.  For example, if the list
        was [2, 3, 1] then it would be a three-layer network, with the
        first layer containing 2 neurons, the second layer 3 neurons,
        and the third layer 1 neuron.  The biases and weights for the
        network are initialized randomly, using a Gaussian
        distribution with mean 0, and variance 1.  Note that the first
        layer is assumed to be an input layer, and by convention we
        won't set any biases for those neurons, since biases are only
        ever used in computing the outputs from later layers."""
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) 
                        for x, y in zip(sizes[:-1], sizes[1:])]

    def feedforward(self, a):
        "Return the output of the network if ``a`` is input."
        for b, w in zip(self.biases, self.weights):
            a = sigmoid_vec(np.dot(w, a)+b)
        return a

    def SGD(self, training_data, epochs, mini_batch_size, eta,
            lmbda, test_data=None):
        """Train the neural network using mini-batch stochastic
        gradient descent.  The ``training_data`` is a list of tuples
        ``(x, y)`` representing the training inputs and the desired
        outputs.  The other non-optional parameters are
        self-explanatory.  If ``test_data`` is provided then the
        network will be evaluated against the test data after each
        epoch, and partial progress printed out.  This is useful for
        tracking progress, but slows things down substantially."""
        if test_data: n_test = len(test_data)
        n = len(training_data)
        for j in xrange(epochs):
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k+mini_batch_size]
                for k in xrange(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.backprop(mini_batch, n, eta, lmbda)
            if test_data:
                print "Epoch {}: {} / {}".format(
                    j, self.evaluate(test_data), n_test)
            else:
                print "Epoch %s complete" % j

    def backprop(self, training_data, n, eta, lmbda):
        """Update the network's weights and biases by applying a
        single iteration of gradient descent using backpropagation.
        The ``training_data`` is a list of tuples ``(x, y)``.  It need
        not include the entire training data set --- it might be a
        mini-batch, or even a single training example.  ``n`` is the
        size of the total training set (which may not be the same as
        the size of ``training_data``).  The other parameters are
        self-explanatory."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        B = len(training_data)
        for x, y in training_data:
            # feedforward
            activation = x
            activations = [x] # list to store all the activations
            zs = [] # list to store all the z vectors
            for b, w in zip(self.biases, self.weights):
                z = np.dot(w, activation)+b
                zs.append(z)
                activation = sigmoid_vec(z)
                activations.append(activation)
            # backward pass
            delta = self.cost_derivative(activations[-1], y) * \
                sigmoid_prime_vec(zs[-1])
            nabla_b[-1] += delta
            nabla_w[-1] += np.dot(delta, activations[-2].transpose())
            # Note that the variable l in the loop below is used a
            # little differently to the book.  Here, l = 1 means the
            # last layer of neurons, l = 2 is the second-last layer,
            # and so on.  It's a renumbering of the scheme used in the
            # book, used to take advantage of the fact that Python can
            # use negative indices in lists.
            for l in xrange(2, self.num_layers):
                z = zs[-l]
                spv = sigmoid_prime_vec(z)
                delta = np.dot(self.weights[-l+1].transpose(), delta) * spv
                nabla_b[-l] += delta
                nabla_w[-l] += np.dot(delta, activations[-l-1].transpose())
        # Add the regularization terms to the gradient for the weights
        nabla_w = [nw+(lmbda*B/n)*w for nw, w in zip(nabla_w, self.weights)]
        self.weights = [w-eta*nw for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-eta*nb for b, nb in zip(self.biases, nabla_b)]

    def evaluate(self, test_data):
        """Return the number of test inputs for which the neural
        network outputs the correct result. Note that the neural
        network's output is assumed to be the index of whichever
        neuron in the final layer has the highest activation."""
        test_results = [(np.argmax(self.feedforward(x)), y) 
                        for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)
        
    def cost(self, x, y):
        """Return the quadratic cost associated to the network, with
        input ``x`` and desired output ``y``.  Note that there is no
        regularization."""
        return np.sum((self.feedforward(x)-y)**2)/2.0

    def cost_derivative(self, output_activations, y):
        """Return the vector of partial derivatives \partial C_x /
        \partial a for the output activations, ``a``.  For the
        unregularized quadratic cost this is just the difference
        between the output activations and the desired output, ``y``."""
        return (output_activations-y) 

#### Miscellaneous functions
def sigmoid(z):
    """The sigmoid function."""
    return 1.0/(1.0+np.exp(-z))

sigmoid_vec = np.vectorize(sigmoid)

def sigmoid_prime(z):
    """Derivative of the sigmoid function."""
    return sigmoid(z)*(1-sigmoid(z))

sigmoid_prime_vec = np.vectorize(sigmoid_prime)
