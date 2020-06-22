""""""
"""
@authors: Deepak Ravikumar Tatachar, Sangamesh Kodge
@copyright: Nanoelectronics Research Laboratory
"""
""""""
import torch
from utils.framework import Framework
from utils.instantiate_model import instantiate_model
from utils.str2bool import str2bool
from utils.boundary_visualization_extension import VisualizeBoundaries
import argparse

parser = argparse.ArgumentParser(description='Train', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# Training parameters
parser.add_argument('--epochs',                 default=100,                type=int,       help='Set number of epochs')
parser.add_argument('--dataset',                default='CIFAR10',          type=str,       help='Set dataset to use')
parser.add_argument('--parallel',               default=False,              type=str2bool,  help='Device in  parallel')
parser.add_argument('--lr',                     default=0.01,               type=float,     help='Learning Rate')
parser.add_argument('--test_accuracy_display',  default=10,                 type=int,       help='Intervals to display test accuracy')
parser.add_argument('--optimizer',              default='SGD',              type=str,       help='Optimizer for training')
parser.add_argument('--loss',                   default='crossentropy',     type=str,       help='loss function for training')
parser.add_argument('--resume',                 default=False,              type=str2bool,  help='resume training from a saved checkpoint')
parser.add_argument('--include_validation',     default=False,              type=str2bool,  help='retrains with validation set')

# Dataloader args
parser.add_argument('--train_batch_size',       default=512,    type=int,       help='Train batch size')
parser.add_argument('--test_batch_size',        default=512,    type=int,       help='Test batch size')
parser.add_argument('--val_split',              default=0.1,    type=float,     help='fraction of training dataset split as validation')
parser.add_argument('--augment',                default=True,   type=str2bool,  help='Random horizontal flip and random crop')
parser.add_argument('--padding_crop',           default=4,      type=int,       help='Padding for random crop')
parser.add_argument('--shuffle',                default=True,   type=str2bool,  help='Shuffle the training dataset')
parser.add_argument('--random_seed',            default=None,   type=int,       help='initialising the seed for reproducibility')

# Model parameters
parser.add_argument('--suffix',         default='',         type=str,        help='appended to model name')
parser.add_argument('--arch',           default='resnet',   type=str,        help='Network architecture')
parser.add_argument('--pretrained',     default=False,      type=str2bool,   help='load saved model for ./pretrained/dataset/')
parser.add_argument('--torch_weights',  default=False,      type=str2bool,   help='load torchvison weights for imagenet')

global args
args = parser.parse_args()
print(args)

def epoch_hook(framework):
    if (framework.current_epoch + 1) % args.test_accuracy_display == 0:
        print("\nEpoch {}: \n Train Loss:{} \n Train Accuracy:{} \n Test Accuracy:{} ".format(framework.current_epoch,
                                                                                              framework.current_train_loss, 
                                                                                              framework.current_train_acc, 
                                                                                              framework.current_test_acc))

if args.dataset.lower()=='imagenet':
    num_classes=1000
elif  args.dataset.lower()=='tinyimagenet':
    num_classes=200
else:
    num_classes=10

net, model_name = instantiate_model(dataset=args.dataset,
                                    num_classes=num_classes, 
                                    arch=args.arch,
                                    suffix=args.suffix, 
                                    load=args.pretrained,
                                    torch_weights=args.torch_weights)

framework = Framework(net=net,
                      model_name=model_name,
                      dataset=args.dataset,
                      epochs=args.epochs,
                      train_batch_size=args.train_batch_size,
                      test_batch_size=args.test_batch_size,
                      val_split=args.val_split,
                      augment=args.augment,
                      padding_crop=args.padding_crop,
                      shuffle=args.shuffle,
                      random_seed=args.random_seed,
                      optimizer=args.optimizer,
                      loss=args.loss,
                      learning_rate=args.lr,
                      adversarial_training=False,
                      device=None)

framework.train(epoch_hook=epoch_hook,
                batch_hook=None)

_ , _, accuracy = framework.test()
print('Test Acc: {}'.format(accuracy))

# Visualization after training, can be done after each batch/epoch by using the epoch_hook or the batch_hook

# Visualize boundaries
# Note you can use this without framework
# You have to use the right arguments when creating the object
# See the constructor for more details
visualization_tool = VisualizeBoundaries(framework=framework)
test_loader = framework.test_loader

for batch_idx, (images, labels) in enumerate(test_loader):
    boundaries = visualization_tool.generate_decision_boundaries(images, 
                                                                 labels,
                                                                 explore_range=40,
                                                                 use_random_dir=False)

    # Show the first image and the decision boundaries around it
    visualization_tool.show(images, boundaries, 0)
    break