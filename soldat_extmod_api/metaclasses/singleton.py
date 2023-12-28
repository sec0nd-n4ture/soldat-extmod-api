import threading

class ClsImplError(Exception):
    def __init__(self) -> None:
        return super().__init__("define all or none of singleton_ref, singleton_set_ref and singleton_detach_ref")

class Singleton(type):
    def __new__(meta_cls, name, bases, dct):
        def default_singleton_ref(cls, *args, **kwargs):
            return cls._singleton_ref

        def default_singleton_set_ref(cls, obj, *args, **kwargs):
            cls._singleton_ref = obj

        def default_singleton_detach_ref(self):
            type(self)._singleton_ref = None

        cls = super().__new__(meta_cls, name, bases, dct)

        has_get_ref_impl = "singleton_ref" in cls.__dict__
        has_set_ref_impl = "singleton_set_ref" in cls.__dict__
        has_detach_ref_impl = "singleton_detach_ref" in cls.__dict__

        if has_get_ref_impl or has_set_ref_impl or has_detach_ref_impl:
            if not has_get_ref_impl or not has_set_ref_impl or not has_detach_ref_impl:
                raise ClsImplError()
        else:
            if not hasattr(cls, "singleton_ref"):
                cls.singleton_ref = classmethod(default_singleton_ref)
            if not hasattr(cls, "singleton_set_ref"):
                cls.singleton_set_ref = classmethod(default_singleton_set_ref)
            if not hasattr(cls, "singleton_detach_ref"):
                cls.singleton_detach_ref = default_singleton_detach_ref

            cls._singleton_ref = None

        cls._singleton_ref_lock = threading.Lock()

        return cls

    def __call__(cls, *args, **kwargs):
        obj = cls.singleton_ref(*args, **kwargs)

        if obj is None:
            with cls._singleton_ref_lock:
                obj = cls.singleton_ref(*args, **kwargs)

                if obj is None:
                    obj = cls.__new__(cls, *args, **kwargs)
                    cls.__init__(obj, *args, **kwargs)

                    cls.singleton_set_ref(obj, *args, **kwargs)

        return obj