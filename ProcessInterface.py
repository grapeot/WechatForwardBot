class ProcessInterface:
    def process(self, msg, type):
        raise NotImplementedError("ProcessInterface is an abstract interface")
