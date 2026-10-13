# Deciphering Structure-Transport Relationships in Multilayer Nanoporous Graphene Membranes for Desalination Using Molecular Dynamics and Interpretable Machine Learning

This project investigates the desalination performance of multilayer nanoporous graphene membranes by combining molecular dynamics (MD), deep reinforcement learning (DRL), and interpretable machine learning. It analyzes the relationship between nanopore structures and transport properties.
The project mainly includes two parts:
Optimizing graphene nanopore structures with DRL to obtain representative pore structures;
Fitting, predicting, and interpreting MD data using XGBoost.


## Requirements
Python 3
Windows, Linux, or macOS
CPU or NVIDIA GPU

## usage

### Train the CNN Model
```
$ python cnn.py
```

After training, the model parameters are saved as:

```
models/
├── resnet_new_flux.ckpt
├── mlp_new_flux.ckpt
├── resnet_new_rej.ckpt
├── mlp_new_rej.ckpt
```

### Train the DRL Agent
```
$ python DQN-GRA.py
```

### Train the XGBoost Model
```
$ python XGBoost.py
```
### DRL Dataset

The dataset used for the DRL component can be generated from PDB files. The corresponding water flux and rejection rate are stored in `id_prop.csv`.

### XGBoost Dataset
The dataset for this component is stored in `pore.xlsx`. The data columns are arranged in the following order: "dG", "H", "O", "Layer", "Pore", "pass-wa", "Na_rejection", "Cl_rejection".
