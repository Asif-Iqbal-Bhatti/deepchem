"""
Loads synthetic reaction datasets from USPTO.

This file contains loaders for synthetic reaction datasets from the US Patent Office. http://nextmovesoftware.com/blog/2014/02/27/unleashing-over-a-million-reactions-into-the-wild/.
"""
import os
import logging
import deepchem
import numpy as np
from deepchem.data import Dataset
from deepchem.molnet.load_function.molnet_loader import _MolnetLoader
from typing import List, Optional, Tuple, Union
import deepchem as dc

logger = logging.getLogger(__name__)

DEFAULT_DIR = deepchem.utils.data_utils.get_data_dir()

USPTO_MIT_URL = "https://deepchemdata.s3.us-west-1.amazonaws.com/datasets/USPTO_MIT.csv"
USPTO_STEREO_URL = "https://deepchemdata.s3.us-west-1.amazonaws.com/datasets/USPTO_STEREO.csv"
USPTO_50K_URL = "https://deepchemdata.s3.us-west-1.amazonaws.com/datasets/USPTO_50K.csv"
USPTO_FULL_URL = "https://deepchemdata.s3.us-west-1.amazonaws.com/datasets/USPTO_FULL.csv"


class _USPTOLoader(_MolnetLoader):

  def __init__(self, *args, subset: str, sep_reagent: bool, **kwargs):
    super(_USPTOLoader, self).__init__(*args, **kwargs)
    self.subset = subset
    self.sep_reagent = sep_reagent
    self.name = 'USPTO_' + subset

  def create_dataset(self) -> Dataset:
    if self.subset not in ['MIT', 'STEREO', '50K', 'FULL']:
      raise ValueError("Valid Subset names are MIT, STEREO and 50K.")

    if self.subset == 'MIT':
      dataset_url = USPTO_MIT_URL

    if self.subset == 'STEREO':
      dataset_url = USPTO_STEREO_URL

    if self.subset == '50K':
      dataset_url = USPTO_50K_URL

    if self.subset == 'FULL':
      dataset_url = USPTO_FULL_URL

    dataset_file = os.path.join(self.data_dir, self.name + '.csv')

    if not os.path.exists(dataset_file):
      logger.info("Downloading dataset...")
      dc.utils.data_utils.download_url(url=dataset_url, dest_dir=self.data_dir)
      logger.info("Dataset download complete.")

    loader = dc.data.CSVLoader(tasks=[], featurizer=self.featurizer)

    return loader.create_dataset(dataset_file, shard_size=8192)


def load_uspto(
    featurizer=None,  # should I remove this?
    splitter: Union[dc.splits.Splitter, str, None] = 'SpecifiedSplitter',
    transformers=None,
    reload: bool = True,
    data_dir: Optional[str] = None,
    save_dir: Optional[str] = None,
    subset: str = "MIT",
    sep_reagent: bool = True,
    **kwargs
) -> Tuple[List[str], Tuple[Dataset, ...], List[dc.trans.Transformer]]:
  """Load USPTO Datasets.

  USPTO is a dataset of over 1.8 Million organic chemical reactions extracted
  from US patents and patent applications. The dataset is stored in the from
  of src and tgt . The src contains the SMILES for the reactants and reagent
  in the form reactant>reagent the tgt contains the SMILES for the product
  SMILES.

  Molnet provides ability to load subsets of USPTO such as MIT, STEREO and 50K.
  The MIT dataset contains around 480k reactions
  The STEREO dataset contains around 1 Million Reactions.
  The 50K dataset contatins 50,000 reactions with an additional label
  indicating the class of reaction to which it belongs. The loader uses the
  specified splitter to use the same splits as used by Schwaller and Coley.
  Custom splitters could also be used. There is also a toggle to load the
  dataset with the reagents separated or mixed.

  Parameters
  ----------
  featurizer: Featurizer or str
    the featurizer to use for processing the data.  Alternatively you can pass
    one of the names from dc.molnet.featurizers as a shortcut.
  splitter: Splitter or str
    the splitter to use for splitting the data into training, validation, and
    test sets.  Alternatively you can pass one of the names from
    dc.molnet.splitters as a shortcut.  If this is None, all the data
    will be included in a single dataset.
  transformers: list of TransformerGenerators or strings
    the Transformers to apply to the data.  Each one is specified by a
    TransformerGenerator or, as a shortcut, one of the names from
    dc.molnet.transformers.
  reload: bool
    if True, the first call for a particular featurizer and splitter will cache
    the datasets to disk, and subsequent calls will reload the cached datasets.
  data_dir: str
    a directory to save the raw data in
  save_dir: str
    a directory to save the dataset in
  subset : str (default 'MIT')
    Subset of dataset to download. 'FULL', 'MIT', 'STEREO', and '50K' are supported.
  Returns
  -------
  tasks, datasets, transformers : tuple
    tasks : list
      Column names corresponding to machine learning target variables.
    datasets : tuple
      train, validation, test splits of data as
      ``deepchem.data.datasets.Dataset`` instances.
    transformers : list
      ``deepchem.trans.transformers.Transformer`` instances applied
      to dataset.
  ----------
  .. [1] Lowe, D.. (2017). Chemical reactions from US patents (1976-Sep2016)
        (Version 1). figshare. https://doi.org/10.6084/m9.figshare.5104873.v1 ([]) 
  .. [2] Schwaller, P., Laino, T., Gaudin, T., Bolgar, P., Hunter, C. A., Bekas,
         C., & Lee, A. A. (2019). Molecular transformer: a model for
         uncertainty-calibrated chemical reaction prediction.
         ACS central science, 5(9), 1572-1583.
  .. [3] Somnath, V. R., Bunne, C., Coley, C. W., Krause, A., & Barzilay, R.
         (2020). Learning Graph Models for Template-Free Retrosynthesis.
         arXiv preprint arXiv:2006.07038.
  .. [4] Dai, H., Li, C., Coley, C. W., Dai, B., & Song, L. (2020).
         Retrosynthesis prediction with conditional graph logic network.
         arXiv preprint arXiv:2001.01408.
  """
  #get test and valid lists if subset is MIT, 50K, STEREO and splitter = specified.
  #if subset is Full use splitter passed by the user.
  #splitter = dc.splits.SpecifiedSplitter(valid_indices=,test_indices=)
  featurizer = dc.feat.UserDefinedFeaturizer([])
  loader = _USPTOLoader(
      featurizer,
      splitter,
      transformers,
      data_dir,
      save_dir,
      subset=subset,
      sep_reagent=sep_reagent,
      **kwargs)
  return loader.load_dataset(loader.name, reload)
