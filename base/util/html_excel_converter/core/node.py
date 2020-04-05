import copy
import weakref


class Node(object):
    def __init__(self, parent=None, children=None, resolved=False, style=None):
        self._resolved = resolved
        self.parent = parent
        self.node_info = None
        self.children = list(children) if children else []
        self.style = style

    def resolve(self, parent, node_info, *args, **kwargs):
        """
        Subclass should implement resolve method.
        :param parent: The parent node.
        :param node_info: Extra information of current node.
        :return: resolved current node.
        """

        r = copy.copy(self)
        r.parent = parent
        r.node_info = node_info
        r._resolved = True
        return r

    @property
    def is_resolved(self):
        return self._resolved

    @property
    def parent(self):
        return self._parent_ref() if self._parent_ref is not None else None

    def get_style(self):
        style = self.parent.get_style() if self.parent is not None else {}
        if self.style is not None:
            style.update(self.style)
        return style

    @parent.setter
    def parent(self, obj):
        if obj is None:
            self._parent_ref = None
        elif isinstance(obj, Node):
            self._parent_ref = weakref.ref(obj)
        else:
            raise TypeError("Parent must be object of Node type.")

    def append_child(self, node):
        if isinstance(node, Node):
            if node.parent is not self and node.parent is not None:
                raise ValueError("Node cannot have more than one parent.")
            node.parent = self
            self.children.append(node)
        else:
            raise TypeError("Child must be object of Node type.")
