import logging

logging.basicConfig(level=logging.INFO)


class AbstractExtractor:
    """Extracts abstract text from a list of elements."""

    def __init__(self):
        """Initialize AbstractExtractor attributes."""
        self.current_section = None  # Keep track of the current section being processed
        self.have_extracted_abstract = (
            False  # Keep track of whether the abstract has been extracted
        )
        self.in_abstract_section = (
            False  # Keep track of whether we're inside the Abstract section
        )
        self.texts = []  # Keep track of the extracted abstract text

    def process(self, element):
        """Process each element and extract abstract text if found.

        Args:
            element (object): An object representing an element.

        Returns:
            bool: True if processing should continue, False otherwise.
        """
        if element.category == "Title":
            self.set_section(element.text)

            if self.current_section == "Abstract":
                self.in_abstract_section = True
                return True

            if self.in_abstract_section:
                return False

        if self.in_abstract_section and element.category == "NarrativeText":
            self.consume_abstract_text(element.text)
            return True

        return True

    def set_section(self, text):
        """Set the current section being processed.

        Args:
            text (str): The text representing the current section.
        """
        self.current_section = text
        logging.info(f"Current section: {self.current_section}")

    def consume_abstract_text(self, text):
        """Append extracted abstract text to the texts list.

        Args:
            text (str): The abstract text to be appended.
        """
        logging.info(f"Abstract part extracted: {text}")
        self.texts.append(text)

    def consume_elements(self, elements):
        """Process a list of elements to extract abstract text.

        Args:
            elements (list): A list of objects representing elements.
        """
        for element in elements:
            should_continue = self.process(element)

            if not should_continue:
                self.have_extracted_abstract = True
                break

        if not self.have_extracted_abstract:
            logging.warning("No abstract found in the given list of objects.")

    def abstract(self):
        """Return the extracted abstract text.

        Returns:
            str: The extracted abstract text.
        """
        return "\n".join(self.texts)
