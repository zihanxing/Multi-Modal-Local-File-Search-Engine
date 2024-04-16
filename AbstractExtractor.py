# Import necessary library
import logging

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)

class AbstractExtractor:
    def __init__(self):
        """
        Initialize the AbstractExtractor object.
        """
        self.current_section = None  # Keep track of the current section being processed
        self.have_extracted_abstract = False  # Keep track of whether the abstract has been extracted
        self.in_abstract_section = False  # Keep track of whether we're inside the Abstract section
        self.texts = []  # Keep track of the extracted abstract text

    def process(self, element):
        """
        Process each element to extract the abstract text.

        Args:
            element: The element to be processed.

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
        """
        Set the current section.

        Args:
            text (str): The text representing the current section.
        """
        self.current_section = text
        logging.info(f"Current section: {self.current_section}")

    def consume_abstract_text(self, text):
        """
        Consume abstract text.

        Args:
            text (str): The abstract text to be consumed.
        """
        logging.info(f"Abstract part extracted: {text}")
        self.texts.append(text)

    def consume_elements(self, elements):
        """
        Consume a list of elements to extract abstract text.

        Args:
            elements (list): List of elements to be processed.
        """
        for element in elements:
            should_continue = self.process(element)

            if not should_continue:
                self.have_extracted_abstract = True
                break

        if not self.have_extracted_abstract:
            logging.warning("No abstract found in the given list of objects.")

    def abstract(self):
        """
        Get the extracted abstract.

        Returns:
            str: The abstract text.
        """
        return "\n".join(self.texts)
