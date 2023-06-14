import torch as th
from torch.nn import functional as F

from rllte.common.base_augmentation import BaseAugmentation


class RandomShift(BaseAugmentation):
    """Random shift operation for processing image-based observations.

    Args:
        pad (int): Padding size.

    Returns:
        Augmented images.
    """

    def __init__(self, pad: int = 4) -> None:
        super().__init__()
        self.pad = pad

    def forward(self, x: th.Tensor) -> th.Tensor:
        n, c, h, w = x.size()
        assert h == w
        padding = tuple([self.pad] * 4)
        x = F.pad(x, padding, "replicate")
        eps = 1.0 / (h + 2 * self.pad)
        arange = th.linspace(-1.0 + eps, 1.0 - eps, h + 2 * self.pad, device=x.device, dtype=x.dtype)[:h]
        arange = arange.unsqueeze(0).repeat(h, 1).unsqueeze(2)
        base_grid = th.cat([arange, arange.transpose(1, 0)], dim=2)
        base_grid = base_grid.unsqueeze(0).repeat(n, 1, 1, 1)

        # TODO: simplify this
        try:
            shift = th.randint(0, 2 * self.pad + 1, size=(n, 1, 1, 2), device=x.device, dtype=x.dtype)
        except Exception:
            shift = th.randint(0, 2 * self.pad + 1, size=(n, 1, 1, 2), dtype=x.dtype).to(x.device)  # for npu device
        shift *= 2.0 / (h + 2 * self.pad)

        grid = base_grid + shift

        return F.grid_sample(x, grid, padding_mode="zeros", align_corners=False)
