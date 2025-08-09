"""
Invoke's own 'binary' entrypoint.

Dogfoods the `program` module.
"""
from types import ModuleType
from typing import Optional, Dict, Any

from invoke import (
    __version__, Program, Collection, Task, CollectionNotFound,
    Exit)
from invoke.config import copy_dict, merge_dicts

from .core import task_namespace


class InvocateCollection(Collection):
    @classmethod
    def from_module(
        cls,
        module: ModuleType,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        loaded_from: Optional[str] = None,
        auto_dash_names: Optional[bool] = None,
    ) -> "Collection":
        """
        Return a new `.Collection` created from ``module``.

        Inspects ``module`` for any `.Task` instances and adds them to a new
        `.Collection`, returning it. If any explicit namespace collections
        exist (named ``ns`` or ``namespace``) a copy of that collection object
        is preferentially loaded instead.

        When the implicit/default collection is generated, it will be named
        after the module's ``__name__`` attribute, or its last dotted section
        if it's a submodule. (I.e. it should usually map to the actual ``.py``
        filename.)

        Explicitly given collections will only be given that module-derived
        name if they don't already have a valid ``.name`` attribute.

        If the module has a docstring (``__doc__``) it is copied onto the
        resulting `.Collection` (and used for display in help, list etc
        output.)

        :param str name:
            A string, which if given will override any automatically derived
            collection name (or name set on the module's root namespace, if it
            has one.)

        :param dict config:
            Used to set config options on the newly created `.Collection`
            before returning it (saving you a call to `.configure`.)

            If the imported module had a root namespace object, ``config`` is
            merged on top of it (i.e. overriding any conflicts.)

        :param str loaded_from:
            Identical to the same-named kwarg from the regular class
            constructor - should be the path where the module was
            found.

        :param bool auto_dash_names:
            Identical to the same-named kwarg from the regular class
            constructor - determines whether emitted names are auto-dashed.

        .. versionadded:: 1.0
        """
        module_name = module.__name__.split(".")[-1]

        def instantiate(obj_name: Optional[str] = None) -> "Collection":
            # Explicitly given name wins over root ns name (if applicable),
            # which wins over actual module name.
            args = [name or obj_name or module_name]
            kwargs = dict(
                loaded_from=loaded_from, auto_dash_names=auto_dash_names
            )
            instance = cls(*args, **kwargs)
            instance.__doc__ = module.__doc__
            return instance

        obj = task_namespace()
        collection = instantiate()
        collection.tasks = collection._transform_lexicon(obj.tasks)
        collection.collections = collection._transform_lexicon(obj.collections)
        collection.default = (
            collection.transform(obj.default) if obj.default else None
        )
        obj_config = copy_dict(obj._configuration)
        if config:
            merge_dicts(obj_config, config)
        collection._configuration = obj_config
        return collection


class InvocateProgram(Program):
    def load_collection(self) -> None:
        """
        Load a task collection based on parsed core args, or die trying.

        .. versionadded:: 1.0
        """
        # NOTE: start, coll_name both fall back to configuration values within
        # Loader (which may, however, get them from our config.)
        start = self.args["search-root"].value
        loader = self.loader_class(  # type: ignore
            config=self.config, start=start
        )
        coll_name = self.args.collection.value
        try:
            module, parent = loader.load(coll_name)
            # This is the earliest we can load project config, so we should -
            # allows project config to affect the task parsing step!
            # TODO: is it worth merging these set- and load- methods? May
            # require more tweaking of how things behave in/after __init__.
            self.config.set_project_location(parent)
            self.config.load_project()
            self.collection = InvocateCollection.from_module(
                module,
                name='',
                loaded_from=parent,
                auto_dash_names=self.config.tasks.auto_dash_names,
            )
        except CollectionNotFound as e:
            raise Exit("Can't find any collection named {!r}!".format(e.name))


program = InvocateProgram(
    name="Invocate",
    binary="invocate",
    binary_names=["invocate"],
    version=__version__,
)