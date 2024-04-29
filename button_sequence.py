from util import format_image_basename


class ButtonSequence:
    """
    Button command sequence data: full text, layer names, composite filename, and origin.
    """
    sequence_mapping: [{}]
    line_number: int
    basename: str = ""

    def __init__(self, mapping, line_no):
        self.sequence_mapping = mapping
        self.line_number = line_no
        self.basename = format_image_basename(self.sequence_mapping)

    @staticmethod
    def to_sequence_mapping_list(button_sequences: ["ButtonSequence"]):
        """
        Extracts a list of button sequence strings, mapping to shortnames, from an input list of ButtonSequences.
        """
        if button_sequences and type(button_sequences[0]) is not ButtonSequence:
            print(
                f"error: can't transform extracted mapping to sequence list, "
                f"unsupported type: {type(button_sequences[0])}")
            return

        result = [seq.sequence_mapping for seq in button_sequences]

        return result
