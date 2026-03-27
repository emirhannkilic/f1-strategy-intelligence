import torch
import torch.nn as nn


class F1StrategyModel(nn.Module):
    def __init__(self, input_dim: int = 13, dropout: float = 0.3):
        super(F1StrategyModel, self).__init__()

        # shared encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
        )

        # pit probability head
        self.pit_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

        # pit window head (start and end lap)
        self.window_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 2)
        )

        # safety car opportunity head
        self.sc_head = nn.Sequential(
            nn.Linear(64, 16), 
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor):
        encoded = self.encoder(x)

        pit_prob = self.pit_head(encoded)
        window = self.window_head(encoded)
        sc_opp = self.sc_head(encoded)

        return pit_prob, window, sc_opp


if __name__ == "__main__":
    model = F1StrategyModel(input_dim=13)
    dummy_input = torch.randn(32, 13)
    pit_prob, window, sc_opp = model(dummy_input)

    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"pit_prob shape: {pit_prob.shape}")
    print(f"window shape:   {window.shape}")
    print(f"sc_opp shape:   {sc_opp.shape}")