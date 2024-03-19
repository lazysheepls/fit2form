# Fit2Form: 3D Generative Model for Robot Gripper Form Design
[Huy Ha](https://www.haquochuy.com/)<sup>\*</sup>,
[Shubham Agrawal](https://bit.ly/3mSuR0d)<sup>\*</sup>,
[Shuran Song](https://www.cs.columbia.edu/~shurans/)
<br>
Columbia University
<br>
[CoRL 2020](https://www.robot-learning.org/)
<br>
<small>*<sup>\*</sup>denotes equal contribution*</small>

### [Project Page](https://fit2form.cs.columbia.edu/) | [Video](https://www.youtube.com/embed/utKHP3qb1bg) | [arXiv](https://arxiv.org/abs/2011.06498)

![](assets/teaser.gif)


## Setup
We've prepared a conda YAML file that contains all the necessary dependencies. To use it, run

```sh
conda env create -f environment.yml
conda activate fit2form
```

## Evaluate a pretrained finger generator
In the repo's root, download the pretrained weights and processed test dataset:
```sh
wget -qO- https://fit2form.cs.columbia.edu/downloads/checkpoints/loss-ablation-checkpoints.tar.xz | tar xvfJ -
mkdir -p downloads/checkpoints; mv *.pth downloads/checkpoints/
wget -qO- https://fit2form.cs.columbia.edu/downloads/data/test.tar.xz | tar xvfJ -
```

Run the following command for evaluation:
```sh
python evaluate_generator.py --evaluate_config configs/evaluate.json --objects test/ --name evaluation_results 
```

## Train a fit2form finger generator
For training a fit2form finger generator, you will need to do the following:
1. Download train-val-test split files
2. Generate dataset
3. Pretrain an AutoEncoder
4. Pretrain the Generator Network 
5. Pretrain the Fitness Network
6. Cotrain Generator and Fitness Network

### 1. Download train-val-test split files
```sh
wget -P data/ https://fit2form.cs.columbia.edu/downloads/data/train_categories.txt
wget -P data/ https://fit2form.cs.columbia.edu/downloads/data/val_categories.txt
wget -P data/ https://fit2form.cs.columbia.edu/downloads/data/test_categories.txt
```

### 2. Generating Datsets
1. Download the [ShapeNetCore dataset](https://www.shapenet.org) and place it in the `data/ShapeNetCore.v2` folder at root. Your data folder should have shapenet category directories like:
```sh
data/
    ShapeNetCore.v2/
        02691156/
        03046257/
        03928116/
        ...
```
2. Generate grasp objects (each object in Shapenet will be dropped from a height, allowed to settle, and then readjusted to our geometry bounds). The generated objects will be stored in the same directory as the original object.
```sh
# - generate collision meshes
python main.py --mode collision_mesh
# - wrap those collision meshes inside urdf files for simulation
python main.py --mode urdf
# - process objects (rescale to bounds) after dropping them from a random orientation
python main.py --mode grasp_objects
```
3. Generate the shapenet-grasp-dataset:
```sh
# Training dataset:
python main.py\
    --name "data/shapenet_grasp_dataset/"\
    --mode pretrain_dataset\
    --split train\
    --train data/train_categories.txt
# Val dataset:
python main.py\
    --name "data/shapenet_grasp_dataset/"\
    --mode pretrain_dataset\
    --split val
    --val data/val_categories.txt
```
4. Generate the imprint-grasp-dataset:
```sh
# - generate imprint fingers
python main.py --mode imprint_baseline
# - simulate grasping using (obj, imprint-left, imprint-right) and store grasping results
#   (a) Training dataset
python main.py\
    --name "data/imprint_grasp_dataset/"\
    --mode pretrain_imprint_dataset 
    --split train\
    --train data/train_categories.txt
#   (b) Val dataset
python main.py\
    --name "data/imprint_grasp_dataset/"\
    --mode pretrain_imprint_dataset 
    --split val\
    --val data/val_categories.txt
```
Note that both modes `pretrain_dataset` and `pretrain_imprint_dataset` produces one million grasp-results by default. You can change this number by passing argument `--num_pretrain_dataset` with desired value.

### 3. Pretrain autoencoder
```sh
python main.py\
    --name train_ae\
    --mode vae\
    --shapenet_train_hdf data/shapenet_grasp_dataset/grasp_results_train.hdf5\
    --shapenet_val_hdf data/shapenet_grasp_dataset/grasp_results_val.hdf5\
    --imprint_train_hdf data/imprint_grasp_dataset/grasp_results_train.hdf5\
    --imprint_val_hdf data/imprint_grasp_dataset/grasp_results_val.hdf5
```

### 4. Pretrain generator network
Replace `<epoch_num>` in the command below:
```sh
python main.py\
    --name pretrain_gn\
    --mode pretrain_gn\
    --ae_checkpoint_path runs/train_ae/vae_<epoch_num>.pth\
    --shapenet_train_hdf data/shapenet_grasp_dataset/grasp_results_train.hdf5\
    --shapenet_val_hdf data/shapenet_grasp_dataset/grasp_results_val.hdf5\
    --imprint_train_hdf data/imprint_grasp_dataset/grasp_results_train.hdf5\
    --imprint_val_hdf data/imprint_grasp_dataset/grasp_results_val.hdf5
```

### 5. Pretrain fitness network
```sh
python main.py\
    --name pretrain_fn\
    --mode pretrain\
    --shapenet_train_hdf data/shapenet_grasp_dataset/grasp_results_train.hdf5\
    --shapenet_val_hdf data/shapenet_grasp_dataset/grasp_results_val.hdf5\
    --imprint_train_hdf data/imprint_grasp_dataset/grasp_results_train.hdf5\
    --imprint_val_hdf data/imprint_grasp_dataset/grasp_results_val.hdf5
```


### 6. Cotraining generator and fitness network 
Replace `<epoch_num>`s in the command below:
```sh
python main.py\
    --name cotrain\
    --mode cotrain\
    --gn_checkpoint_path runs/pretrain_gn/imprint_pretrain_gn_<epoch_num>.pth\
    --fn_checkpoint_path runs/pretrain_fn/pretrain_<epoch_num>.pth\
    --shapenet_train_hdf data/shapenet_grasp_dataset/grasp_results_train.hdf5\
    --shapenet_val_hdf data/shapenet_grasp_dataset/grasp_results_val.hdf5\
    --imprint_train_hdf data/imprint_grasp_dataset/grasp_results_train.hdf5\
    --imprint_val_hdf data/imprint_grasp_dataset/grasp_results_val.hdf5
```

## Citation
```
@inproceedings{ha2020fit2form,
    title={{Fit2Form}: 3{D} Generative Model for Robot Gripper Form Design},
    author={Ha, Huy and Agrawal, Shubham and Song, Shuran},
    booktitle={Conference on Robotic Learning (CoRL)},
    year={2020} 
}
```
