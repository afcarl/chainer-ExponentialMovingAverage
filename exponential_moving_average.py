import chainer
from chainer import configuration
from chainer import link


class ExponentialMovingAverage(link.Chain):

    def __init__(self, target, decay=0.999):
        super(ExponentialMovingAverage, self).__init__()
        self.decay = decay
        with self.init_scope():
            self.target = target
            self.ema = target.copy()
            with self.ema.init_scope():
                for name, param in target.namedparams():
                    name = name[1:]  # remove prefix
                    setattr(self.ema, name, chainer.Parameter(param.array))

    def __call__(self, *args, **kwargs):
        if configuration.config.train:
            ys = self.target(*args, **kwargs)
            for name, target_param in self.target.namedparams():
                name = name[1:]  # remove prefix
                ema_param = getattr(self.ema, name)
                if (not target_param.requires_grad
                        or ema_param.array is None):
                    new_average = target_param.array
                else:
                    new_average = self.decay * target_param.array + \
                        (1 - self.decay) * ema_param.array
                with self.ema.init_scope():
                    setattr(self.ema, name, chainer.Parameter(new_average))
        else:
            ys = self.ema(*args, **kwargs)
        return ys
