from system_learning.meta_learning.meta_learning_bus import get_process_bus


class MetaLearningBus:
    @staticmethod
    def get_instance():
        return get_process_bus()
