# Copyright (c) OpenMMLab. All rights reserved.
from typing import Any, Dict, List

import numpy as np


class CRD_ClsDatasetMixin(object):
    """Dataset mixin for CRD algorithm on classification datasets.

    Args:
        neg_num (int, optional): Number of negative samples. Defaults to 16384.
        sample_mode (str, optional): Sample mode. Defaults to 'exact'.
        percent (float, optional): Sampling percentage. Defaults to 1.0.
    """

    def __init__(self,
                 neg_num: int = 16384,
                 sample_mode: str = 'exact',
                 percent: float = 1.0) -> None:

        self._parse_fullset_contrast_info(neg_num, sample_mode, percent)

    def _parse_fullset_contrast_info(self, neg_num: int, sample_mode: str,
                                     percent: float) -> None:
        """parse contrast information of the whole dataset.

        Args:
            neg_num (int): negative sample number.
            sample_mode (str): sample mode.
            percent (float): sampling percentage.
        """
        assert sample_mode in ['exact', 'random']
        num_classes: int = len(self.CLASSES)  # type: ignore
        if not self.test_mode:  # type: ignore
            # Must fully initialize dataset first.
            self.full_init()  # type: ignore

            # Parse info.
            self.gt_labels = [data['gt_label']
                              for data in self.data_list]  # type: ignore
            self.neg_num = neg_num
            self.sample_mode = sample_mode
            self.num_samples = self.__len__()  # type: ignore

            self.cls_positive: List[List[int]] = [[]
                                                  for i in range(num_classes)]
            for i in range(self.num_samples):
                self.cls_positive[self.gt_labels[i]].append(i)

            self.cls_negative: List[List[int]] = [[]
                                                  for i in range(num_classes)]
            for i in range(num_classes):
                for j in range(num_classes):
                    if j == i:
                        continue
                    self.cls_negative[i].extend(self.cls_positive[j])

            self.cls_positive = [
                np.asarray(self.cls_positive[i]) for i in range(num_classes)
            ]
            self.cls_negative = [
                np.asarray(self.cls_negative[i]) for i in range(num_classes)
            ]

            if 0 < percent < 1:
                n = int(len(self.cls_negative[0]) * percent)
                self.cls_negative = [
                    np.random.permutation(self.cls_negative[i])[0:n]
                    for i in range(num_classes)
                ]

            self.cls_positive = np.asarray(self.cls_positive)
            self.cls_negative = np.asarray(self.cls_negative)

    def _get_contrast_info(self, data: Dict, idx: int) -> Dict:
        """Get contrast information for each data sample."""
        if self.sample_mode == 'exact':
            pos_idx = idx
        elif self.sample_mode == 'random':
            pos_idx = np.random.choice(self.cls_positive[self.gt_labels[idx]],
                                       1)
            pos_idx = pos_idx[0]  # type: ignore
        else:
            raise NotImplementedError(self.sample_mode)
        replace = True if self.neg_num > \
            len(self.cls_negative[self.gt_labels[idx]]) else False
        neg_idx = np.random.choice(
            self.cls_negative[self.gt_labels[idx]],
            self.neg_num,
            replace=replace)
        contrast_sample_idxs = np.hstack((np.asarray([pos_idx]), neg_idx))
        data['contrast_sample_idxs'] = contrast_sample_idxs
        return data

    def prepare_data(self, idx) -> Any:
        """Get data processed by ``self.pipeline``.

        Args:
            idx (int): The index of ``data_info``.
        Returns:
            Any: Depends on ``self.pipeline``.
        """
        data_info = self.get_data_info(idx)  # type: ignore
        if not self.test_mode:  # type: ignore
            data_info = self._get_contrast_info(data_info, idx)
        return self.pipeline(data_info)  # type: ignore