import os
import shutil



def move_txt():
    source_dir = '/kaggle/input/tinyshakespeare'
    destination_dir = '/kaggle/working/'

    # Ensure the destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    # List all .pt files in the source directory
    checkpoint_files = [f for f in os.listdir(source_dir) if f.endswith('.txt')]

    if not checkpoint_files:
        print("No txt files found!")
        return

    for file in checkpoint_files:
        source_path = os.path.join(source_dir, file)
        destination_path = os.path.join(destination_dir, 'tinyshakespeare.txt')

        if os.path.exists(destination_path):
            print(f"File {file} already exists in destination, skipping!")
        else:
            shutil.copy(source_path, destination_path)
            print(f"Moved {file} successfully!")

# Execute the function
move_txt()

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Check device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("Using device:", device)

# Hyperparameters
batch_size   = 64 #the number of parallel computations over which gradients will be computed.
seq_length   = 100 #The length of the input layer.
hidden_size  = 256 # No. of hidden units in the hidden layer of the LSTM. 
num_layers   = 2 # How many stacked LSTM layers are there.
num_epochs   = 20
learning_rate = 0.002


# ------------------------------
# 1. Load and preprocess the data
# ------------------------------
with open('tinyshakespeare.txt', 'r') as f:
    text = f.read()

# Build character-level vocabulary
chars = sorted(list(set(text)))
vocab_size = len(chars) # The total number of characters the model plays with.
print(f"Vocabulary size: {vocab_size}")

# Mappings from characters to integers and vice versa
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for i, ch in enumerate(chars)}

# Encode entire text into a numpy array of integers
data = np.array([stoi[c] for c in text], dtype=np.int64)

# Split data: 90% training, 10% validation
split_idx = int(0.9 * len(data))
train_data = data[:split_idx]
val_data = data[split_idx:]
print(f"Train data length: {len(train_data)}, Val data length: {len(val_data)}")



# ------------------------------
# 2. Create a batch generator
# ------------------------------



def get_batch(data, batch_size, seq_length): 
    # data = train_data, for example
    # Calculate how many full batches we can make
    num_batches = len(data) // (batch_size * seq_length)
    # Trim data so that it divides evenly into batches
    data = data[:num_batches * batch_size * seq_length]
    # Reshape into (batch_size, -1) so that each row is a continuous stream of tokens
    data = data.reshape((batch_size, -1))
    
    # Yield batches sequentially
    for i in range(0, data.shape[1] - seq_length, seq_length):
        x = data[:, i:i+seq_length]
        y = data[:, i+1:i+seq_length+1]  # targets are shifted by one
        yield torch.tensor(x, dtype=torch.long).to(device), torch.tensor(y, dtype=torch.long).to(device)


# ------------------------------
# 3. Define the RNN model
# ------------------------------
class CharRNN(nn.Module):
    def __init__(self, vocab_size, hidden_size, num_layers):
        super(CharRNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # This describes 2 layers of NN with vocab_size and hidden_size number of nodes, respectively.
        self.embed = nn.Embedding(vocab_size, hidden_size)
        
        # LSTM layer: a common choice for sequence tasks
        # The first hidden_size is there because it connects to the Embedding layer.
        # The second tells the size of each layer of the LSTM.
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers, batch_first=True)
        # Final linear layer to map hidden states to the vocabulary space
        self.fc = nn.Linear(hidden_size, vocab_size) # fc stands for fully connected.
    
    def forward(self, x, hidden):
        #hidden from the past affects the output!
        # x: (batch, seq_length)
        x = self.embed(x)  # -> (batch, seq_length, hidden_size)
        out, hidden = self.lstm(x, hidden)
        # out: (batch, seq_length, hidden_size)
        out = self.fc(out)  # -> (batch, seq_length, vocab_size)
        return out, hidden
    
    def init_hidden(self, batch_size):
        # Initialize hidden state and cell state with zeros
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return (h0, c0)


model = CharRNN(vocab_size, hidden_size, num_layers).to(device)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
criterion = nn.CrossEntropyLoss()

# ------------------------------
# 4. Training Loop
# ------------------------------
# Determine number of training steps per epoch
n_steps = len(train_data) // (batch_size * seq_length) #n_steps is the number of steps that will be required to see the full data once.
print("Training steps per epoch:", n_steps)

for epoch in range(num_epochs):
    model.train()
    hidden = model.init_hidden(batch_size)
    total_loss = 0.0

    # Create a new batch generator for each epoch
    for step, (x_batch, y_batch) in enumerate(get_batch(train_data, batch_size, seq_length)):
        # Detach hidden state to prevent backpropagating through the entire history
        hidden = tuple([h.detach() for h in hidden])
        optimizer.zero_grad()
        outputs, hidden = model(x_batch, hidden)
        # Reshape outputs to (batch_size*seq_length, vocab_size) for CrossEntropyLoss
        loss = criterion(outputs.view(-1, vocab_size), y_batch.view(-1))
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        if (step + 1) % 100 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}], Step [{step+1}/{n_steps}], Loss: {loss.item():.4f}")
    
    avg_loss = total_loss / n_steps
    print(f"Epoch [{epoch+1}/{num_epochs}] Average Training Loss: {avg_loss:.4f}")
    
    # ------------------------------
    # Validation after each epoch
    # ------------------------------
    model.eval()
    with torch.no_grad():
        val_hidden = model.init_hidden(batch_size)
        val_loss = 0.0
        val_steps = len(val_data) // (batch_size * seq_length)
        for x_val, y_val in get_batch(val_data, batch_size, seq_length):
            val_hidden = tuple([h.detach() for h in val_hidden])
            outputs, val_hidden = model(x_val, val_hidden)
            loss = criterion(outputs.view(-1, vocab_size), y_val.view(-1))
            val_loss += loss.item()
            # Limit the number of validation steps to cover the dataset once
            if (val_steps := val_steps - 1) <= 0:
                break
        avg_val_loss = val_loss / (len(val_data) // (batch_size * seq_length))
        print(f"Epoch [{epoch+1}/{num_epochs}] Validation Loss: {avg_val_loss:.4f}")

# ------------------------------
# 5. Text Generation
# ------------------------------
def generate_text(model, start_str, gen_length=200, temperature=1.0):
    """
    Generate text given a starting string.
    - temperature: controls randomness. Lower -> more deterministic.
    """
    model.eval()
    # Convert start string to tensor indices
    input_seq = torch.tensor([stoi[c] for c in start_str], dtype=torch.long).unsqueeze(0).to(device)
    hidden = model.init_hidden(1)
    generated = start_str

    with torch.no_grad():
        for _ in range(gen_length):
            outputs, hidden = model(input_seq, hidden)
            # Get logits for the last character in the sequence
            logits = outputs[:, -1, :] / temperature
            # Sample from the distribution
            probs = torch.softmax(logits, dim=-1)
            next_idx = torch.multinomial(probs, num_samples=1).item()
            next_char = itos[next_idx]
            generated += next_char
            # Prepare next input (use only the most recent predicted character)
            input_seq = torch.tensor([[next_idx]], dtype=torch.long).to(device)
    return generated

# Generate and print text using a seed string
seed_text = "To be, or not to be, "
generated_text = generate_text(model, start_str=seed_text, gen_length=300, temperature=0.8)
print("\nGenerated Text:")
print(generated_text)
