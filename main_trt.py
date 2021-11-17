import numpy as np
import argparse

from trt_lib.Interface import Interface as trtInterface
from importable_main import import_data
from data_worker.data_worker import split_into_batches
from torch_lib.data_worker import suit4torch
from torch_lib.Interface import Interface as torchInterface
from torch_lib.Nets import LargeNet as torchLNet, \
    MediumNet as torchMNet, SmallNet as torchSNet


def get_args():

    parser = argparse.ArgumentParser(
        description="Mode selection through flags")
    parser.add_argument(
        '-eo', '--export_onnx', action="store_true",
        help="select export onnx mode", default=False)
    parser.add_argument(
        '-pth', '--path', help="path for onnx or trt file", type=str)
    parser.add_argument(
        '-s', '--size', help="net size", type=str)
    parser.add_argument(
        '-p', '--priority', help="execution priority", type=int, default=0)
    parser.add_argument(
        '-f', '--framework', help="select framework", type=str,
        default='torch')
    parser.add_argument(
        '-d', '--device', help="select device", type=str,
        default='cpu')
    parser.add_argument(
        '-bs', '--batch_size', help='select batch size', type=int, default=10)
    args = parser.parse_args()
    return vars(args)


def export_onnx_main(path, size, framework, batch_size, **kwargs):

    X_data, Y_data = import_data()
    X, Y = suit4torch(X_data, Y_data)
    batches = split_into_batches(X, Y, batch_size)
    dummy_batch, _ = batches[0]

    net = torchSNet()
    if size == 'small_v1':
        net = torchSNet()
    elif size == 'medium_v1':
        net = torchMNet()
    elif size == 'large_v1':
        net = torchLNet()
    net_interface = torchInterface(net)
    net_interface.load_weights(
        f'saved_nets/saved_{framework}/{size}.pth')

    net_interface.convert2onnx(path, dummy_batch)


def run_trt_main(batch_size, path):

    target_dtype = np.float32

    X_data, Y_data = import_data()

    X, Y = suit4torch(X_data, Y_data)
    # batch_size = 10
    batches = split_into_batches(X, Y, batch_size)
    X, Y = batches[0]

    X = X.float()
    Y = Y.float()

    X = np.array(X, dtype=target_dtype)
    Y = np.array(Y, dtype=target_dtype)
    X = np.ascontiguousarray(X)

    # path = "saved_nets/saved_onnx/torch_small_v1.trt"

    net_interface = trtInterface(
        path, X, batch_size=batch_size, n_classes=10,
        target_dtype=target_dtype)

    Y_pred = net_interface.predict_net(X)

    print(Y_pred)


if __name__ == "__main__":

    kwargs = get_args()

    if kwargs['export_onnx']:
        export_onnx_main(**kwargs)
    else:
        run_trt_main(**kwargs)
