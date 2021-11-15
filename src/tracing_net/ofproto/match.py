from src.api.proto import net_pb2


class Match:
    """A OpenFlow Match Class


    TODO:
        * __eq__ を実装
    """

    def __init__(self, field_name=None, value=None, mask=None):
        self.field_name = field_name
        self.value = value
        self.mask = mask

    @property
    def masked_value(self):
        """
           * IPアドレスのマスクをどう実装するか？？？
           * 値をどうするのか
        Returns:
            int or
        """
        raise NotImplementedError

    def is_match(self, value):
        """Does the value match?

        Returns:
            bool
        """
        if isinstance(value, str) and value.isdigit():
            value = int(value)

        if value == self.value:
            return True
        else:
            return False

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Match
        """
        match = net_pb2.Match()
        match.field_name = self.field_name
        match.value = str(self.value)
        match.mask = str(self.mask)
        return match

    def __repr__(self):
        return "<{}, {}/{}>".format(self.field_name, self.value, self.mask)