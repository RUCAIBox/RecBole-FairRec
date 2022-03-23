import os
import sys
import pytorch_lightning as pl
import argparse
import pytorch_lightning.callbacks as plc
from pytorch_lightning import Trainer
from torch.utils.tensorboard import summary

from model import ModelInterface, Classifier
from data import DataInterface


def load_callbacks():
    callbacks = []

    callbacks.append(plc.EarlyStopping(
        monitor='valid/auc',
        # monitor='valid/f1_micro',
        mode='min',
        patience=5,
        min_delta=0.001,
        verbose=True,
        strict=True
    ))

    callbacks.append(plc.ModelCheckpoint(
        filename='{epoch:03d}-{valid/auc:.3f}',
        save_top_k=1,
        monitor='valid/auc',
        mode='max',
        save_last=True,
        verbose=True,
        auto_insert_metric_name=False,
    ))

    return callbacks


def main(args):
    pl.seed_everything(seed=2022521)
    
    data_module = DataInterface(args.data_path, args.sst, args.batch_size)
    model = Classifier(args.input_dim, args.output_dim, args.dropout, args.activation)
    model_mudule = ModelInterface(model, args)

    trainer = Trainer.from_argparse_args(args, callbacks=load_callbacks())
    trainer.fit(model_mudule, data_module)
    trainer.test(model_mudule, data_module)


if __name__ == '__main__':
    os.chdir(sys.path[0])

    parser = argparse.ArgumentParser()

    parser.add_argument('--data_path', type=str, default='../dataset/PFCN_MLP_embed-[gender_age_occupation]_none.pth')
 
    parser.add_argument('--input_dim', type=int, default=64)
    parser.add_argument('--output_dim', type=int, default=21)
    parser.add_argument('--batch_size', type=int, default=1024)
    parser.add_argument('--weight_decay', type=float, default=1e-4)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--dropout', type=float, default=0.3)
    parser.add_argument('--sst', type=str, default='occupation')
    parser.add_argument('--activation', type=str, default='leakyrelu')

    parser = Trainer.add_argparse_args(parser)

    parser.set_defaults(max_epochs=300)
    # parser.set_defaults(gpus=[0])
    parser.set_defaults(log_every_n_steps=24)
    parser.set_defaults(check_val_every_n_epoch=10)

    args = parser.parse_args()

    main(args)

