import sys

import numpy as np
import pytest
from anndata import AnnData

import enhancerai as enhai


def test_package_has_version():
    assert enhai.__version__ is not None


def test_import_topics_shape():
    ann_data = enhai.import_topics(
        topics_folder="tests/data/test_topics",
        regions_file="tests/data/test.regions.bed",
    )
    # Test type
    assert isinstance(ann_data, AnnData)

    # Test shape
    expected_number_of_topics = 3
    expected_number_of_peaks = 23186

    assert ann_data.shape == (expected_number_of_topics, expected_number_of_peaks)

    # Test columns
    assert "file_path" in ann_data.obs.columns
    assert "n_open_regions" in ann_data.obs.columns
    assert "n_topics" in ann_data.var.columns


def test_import_topics_topics_subset():
    ann_data = enhai.import_topics(
        topics_folder="tests/data/test_topics",
        regions_file="tests/data/test.regions.bed",
        topics_subset=["Topic_1", "Topic_2"],
    )
    assert ann_data.shape[0] == 2


def test_import_topics_invalid_files():
    with pytest.raises(FileNotFoundError):
        enhai.import_topics(topics_folder="invalid_folder", regions_file="invalid_file")


def test_import_topics_compression():
    ann_data_c = enhai.import_topics(
        topics_folder="tests/data/test_topics",
        regions_file="tests/data/test.regions.bed",
        compress=True,
    )
    assert ann_data_c.X.getformat() == "csr"
    assert ann_data_c.X.shape == (3, 23186)

    ann_data = enhai.import_topics(
        topics_folder="tests/data/test_topics",
        regions_file="tests/data/test.regions.bed",
        compress=False,
    )
    assert isinstance(ann_data.X, np.ndarray)
    assert ann_data.X.shape == (3, 23186)

    assert sys.getsizeof(ann_data_c.X) < sys.getsizeof(ann_data.X)


def test_import_topics_chromsizes():
    ann_data = enhai.import_topics(
        topics_folder="tests/data/test_topics",
        regions_file="tests/data/test.regions.bed",
        chromsizes_file="tests/data/test.chrom.sizes",
        compress=True,
    )
    expected_removed_regions = ["chr19:60789836-60790336"]
    for region in expected_removed_regions:
        assert region not in list(ann_data.var.index)
