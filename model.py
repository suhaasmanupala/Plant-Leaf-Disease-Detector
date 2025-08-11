
import torch.nn as nn
import torch.nn.functional as F

class SimplePlantDiseaseCNN(nn.Module):
    def __init__(self, num_classes):
        super(SimplePlantDiseaseCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2,2)
        self.dropout = nn.Dropout(0.25)
        self.fc1 = nn.Linear(64 * 28 * 28, 128)  # Assumes input image size is 224x224
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))   # 112x112
        x = self.pool(F.relu(self.conv2(x)))   # 56x56
        x = self.pool(F.relu(self.conv3(x)))   # 28x28
        x = x.view(-1, 64 * 28 * 28)
        x = self.dropout(x)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x
