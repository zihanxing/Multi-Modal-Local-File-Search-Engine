import logging

logging.basicConfig(level=logging.INFO)


class AbstractExtractor:
    def __init__(self):
        self.current_section = None  # Keep track of the current section being processed
        self.have_extracted_abstract = (
            False  # Keep track of whether the abstract has been extracted
        )
        self.in_abstract_section = (
            False  # Keep track of whether we're inside the Abstract section
        )
        self.texts = []  # Keep track of the extracted abstract text

    def process(self, element):
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
        self.current_section = text
        logging.info(f"Current section: {self.current_section}")

    def consume_abstract_text(self, text):
        logging.info(f"Abstract part extracted: {text}")
        self.texts.append(text)

    def consume_elements(self, elements):
        for element in elements:
            should_continue = self.process(element)

            if not should_continue:
                self.have_extracted_abstract = True
                break

        if not self.have_extracted_abstract:
            logging.warning("No abstract found in the given list of objects.")

    def abstract(self):
        return "\n".join(self.texts)