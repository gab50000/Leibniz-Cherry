class HTMLList(list):
    def __str__(self):
        return "<ul>\n" + "\n".join(f"  <li> {x} </li>" for x in self) + "\n</ul>"

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        list_ = super().__add__(other)
        return HTMLList(list_)

    def __radd__(self, other):
        return self.__add__(other)


