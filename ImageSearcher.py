import numpy as np
import scipy
import sys
import logging
import hashlib
import sys

# Caffe related configurations
caffe_root = './DouTuRobot/caffe/'

# Old model: googlenet
#model_prototxt = caffe_root + 'models/bvlc_googlenet/deploy.prototxt'
#model_trained = caffe_root + 'models/bvlc_googlenet/bvlc_googlenet.caffemodel'
#layer_name = 'pool5/7x7_s1'
# New model: caffenet
model_prototxt = caffe_root + 'models/bvlc_reference_caffenet/deploy.prototxt'
model_trained = caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'
layer_name = 'fc8'

imagenet_labels = caffe_root + 'data/ilsvrc12/synset_words.txt'
mean_path = caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy'
sys.path.insert(0, caffe_root + 'python')
import caffe
caffe.set_mode_cpu()
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class ImageSearcher:
    def __init__(self, featurefn):
        self.resultNum = 5
        self.net = caffe.Classifier(model_prototxt, model_trained,
            mean=np.load(mean_path).mean(1).mean(1),
            channel_swap=(2,1,0),
            raw_scale=255,
            image_dims=(256, 256))
        self.parseFeature(featurefn)
        logging.info('Caffe net initialized. Loading cache...')
        #self.buildCache()
        self.loadCache('./featureCache.tsv')
        logging.info('Cache built.')

    def loadCache(self, fn):
        lines = [ x.strip().split('\t') for x in open(fn) ]
        self.resultCache = { x[0]: x[1].split(',') for x in lines }

    # Precompute the SHA-SearchResult cache
    def buildCache(self):
        for i in range(self.features.shape[0]):
            qfeature = self.features[i, :]
            results = self.searchWithFeature(qfeature)
            self.resultCache[self.hashes[i]] = results
            sys.stderr.write('.')
        sys.stderr.write('\n')
    
    # The feature file is expected to have three columns: id (usually file name), md5, and DNN features
    def parseFeature(self, fn):
        features = []
        self.imgfns = []
        self.hashes = []
        for line in open(fn):
            imgfn, hash, imgfeatures = line.split('\t')
            features.append([ float(x) for x in imgfeatures.split(' ') ])
            self.hashes.append(hash)
            self.imgfns.append(imgfn)
        self.features = np.asarray(features)
        self.resultCache = {}

    # Return the features extracted from the file
    def extractFeatures(self, fn):
        input_image = caffe.io.load_image(fn)
        self.net.predict([input_image], oversample=False)
        feature = self.net.blobs[layer_name].data[0]
        return feature

    def searchWithFeature(self, queryFeature):
        disp = self.features - queryFeature
        distances = (disp * disp).sum(1)
        indices = np.argsort(distances)
        if distances[indices[0]] < 0.02:
            # very close. We don't want to send dups
            index = indices[1: 1 + self.resultNum]
        else:
            index = indices[0: self.resultNum]
        return [ self.imgfns[i] for i in index ]

    # Search for the most similar image to the given query
    def search(self, fn):
        # First check the cache
        with open(fn, 'rb') as fp:
            cachekey = hashlib.sha224(fp.read()).hexdigest()
        if cachekey in self.resultCache:
            logging.info('Cache hit! Directly return.')
            return self.resultCache[cachekey]
        # Cache miss. Search and update cache
        queryFeature = self.extractFeatures(fn).reshape(1, -1)
        result = self.searchWithFeature(queryFeature)
        self.resultCache[cachekey] = result
        return result

if __name__ == '__main__':
    imageSearcher = ImageSearcher('./DoutuFeatures.txt')
    print(imageSearcher.search('./DouTuRobot/dat/jpgs/170405-013811.gif.jpg'))
    print(imageSearcher.search('./DouTuRobot/dat/jpgs/170405-013811.gif.jpg'))
