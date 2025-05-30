import numpy as np

# data I/O
data = open('input.txt', 'r').read() # should be simple plain text file

# use set() to count the vacab size
chars = list(set(data))
data_size, vocab_size = len(data), len(chars)

# The original code was written in some ancient version of python
print(f"data has {data_size} characters, {vocab_size} unique.") 

# dictionary to convert char to idx, idx to char
char_to_ix = { ch:i for i,ch in enumerate(chars) }
ix_to_char = { i:ch for i,ch in enumerate(chars) }

print(char_to_ix)
print(ix_to_char)

# hyperparameters
hidden_size = 100 # size of hidden layer of neurons
seq_length = 25 # number of steps to unroll the RNN for. P:?
learning_rate = 1e-1
