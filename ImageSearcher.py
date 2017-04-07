import numpy as np
import scipy
import sys
import logging

# Caffe related configurations
caffe_root = './DouTuRobot/caffe/'
model_prototxt = caffe_root + 'models/bvlc_googlenet/deploy.prototxt'
model_trained = caffe_root + 'models/bvlc_googlenet/bvlc_googlenet.caffemodel'
imagenet_labels = caffe_root + 'data/ilsvrc12/synset_words.txt'
mean_path = caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy'
layer_name = 'pool5/7x7_s1'
sys.path.insert(0, caffe_root + 'python')
import caffe
caffe.set_mode_cpu()
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class ImageSearcher:
    def __init__(self, featurefn):
        self.parseFeature(featurefn)
        self.net = caffe.Classifier(model_prototxt, model_trained,
            mean=np.load(mean_path).mean(1).mean(1),
            channel_swap=(2,1,0),
            raw_scale=255,
            image_dims=(256, 256))
        logging.info('Caffe net initialized.')
    
    def parseFeature(self, fn):
        features = []
        self.imgfns = []
        for line in open(fn):
            imgfn, imgfeatures = line.split('\t')
            features.append([ float(x) for x in imgfeatures.split(' ') ])
            self.imgfns.append(imgfn)
        self.features = np.asarray(features)

    # Return the features extracted from the file
    def extractFeatures(self, fn):
        input_image = caffe.io.load_image(fn)
        self.net.predict([input_image], oversample=False)
        feature = self.net.blobs[layer_name].data[0]
        return feature

    # Search for the most similar image to the given query
    def search(self, fn):
        queryFeature = self.extractFeatures(fn).reshape(1, -1)
        disp = self.features - queryFeature
        distances = (disp * disp).sum(1)
        indices = np.argsort(distances)
        if distances[indices[0]] < 0.01:
            # very close. We don't want to send dups
            index = indices[1]
        else:
            index = indices[0]
        return self.imgfns[index]

if __name__ == '__main__':
    imageSearcher = ImageSearcher('./featuresall.txt')
    print(imageSearcher.search('dat/jpgs/170405-013811.gif.jpg'))
