import torch
import torch.nn as nn
import torch.nn.functional as F


class SC2QNet(nn.Module):

    def __init__(self,
                 resolution,
                 n_channels_screen,
                 n_channels_minimap,
                 n_out,
                 batchnorm=False):
        super(SC2QNet, self).__init__()
        self.screen_conv1 = nn.Conv2d(in_channels=n_channels_screen,
                                      out_channels=16,
                                      kernel_size=5,
                                      stride=1,
                                      padding=2)
        self.screen_conv2 = nn.Conv2d(in_channels=16,
                                      out_channels=32,
                                      kernel_size=3,
                                      stride=1,
                                      padding=1)
        self.minimap_conv1 = nn.Conv2d(in_channels=n_channels_minimap,
                                       out_channels=16,
                                       kernel_size=5,
                                       stride=1,
                                       padding=2)
        self.minimap_conv2 = nn.Conv2d(in_channels=16,
                                       out_channels=32,
                                       kernel_size=3,
                                       stride=1,
                                       padding=1)
        if batchnorm:
            self.screen_bn1 = nn.BatchNorm2d(16)
            self.screen_bn2 = nn.BatchNorm2d(32)
            self.minimap_bn1 = nn.BatchNorm2d(16)
            self.minimap_bn2 = nn.BatchNorm2d(32)
            self.player_bn = nn.BatchNorm2d(10)
        self.state_fc = nn.Linear(74 * (resolution ** 2), 256)
        self.q_fc = nn.Linear(256, n_out)
        self._batchnorm = batchnorm

    def forward(self, x):
        screen, minimap, player = x
        player = player.clone().repeat(
            screen.size(2), screen.size(3), 1, 1).permute(2, 3, 0, 1)
        if self._batchnorm:
            screen = F.leaky_relu(self.screen_bn1(self.screen_conv1(screen)))
            screen = F.leaky_relu(self.screen_bn2(self.screen_conv2(screen)))
            minimap = F.leaky_relu(self.minimap_bn1(self.minimap_conv1(minimap)))
            minimap = F.leaky_relu(self.minimap_bn2(self.minimap_conv2(minimap)))
            player = self.player_bn(player.contiguous())
        else:
            screen = F.leaky_relu(self.screen_conv1(screen))
            screen = F.leaky_relu(self.screen_conv2(screen))
            minimap = F.leaky_relu(self.minimap_conv1(minimap))
            minimap = F.leaky_relu(self.minimap_conv2(minimap))
        screen_minimap = torch.cat((screen, minimap, player), 1)
        state = F.leaky_relu(self.state_fc(
            screen_minimap.view(screen_minimap.size(0), -1)))
        return self.q_fc(state)
